from django.test import SimpleTestCase
from django.db import models

from robber import expect

from es_index.queries.utils import (
    join_expression, field_name_with_alias, is_model_subclass, clean_db_type
)


class TestUtilsAuthor(models.Model):
    class Meta:
        app_label = 'es_index'


class TestUtilsPaper(object):
    class Meta:
        app_label = 'es_index'


class UtilsTestCase(SimpleTestCase):
    def test_join_expression(self):
        expect(
            join_expression(
                'data_article',
                'article',
                'author_id',
                'author',
                'id'
            )
        ).to.eq(
            'LEFT JOIN data_article article ON article.author_id = author.id'
        )

    def test_field_name_with_alias(self):
        expect(
            field_name_with_alias('base_table', 'officer.id')
        ).to.eq('officer.id')

        expect(
            field_name_with_alias('base_table', 'name')
        ).to.eq('base_table.name')

    def test_is_model_subclass(self):
        expect(is_model_subclass(TestUtilsAuthor)).to.be.true()
        expect(is_model_subclass(TestUtilsPaper)).to.be.false()

    def test_clean_db_type(self):
        expect(clean_db_type('numeric(5, 2)')).to.eq('numeric')
        expect(clean_db_type('varchar(50)')).to.eq('varchar')
        expect(clean_db_type('timestamp with time zone')).to.eq('timestamp with time zone')
