from robber import expect
from django.test import TestCase

from officers.doc_types import OfficerInfoDocType
from search.tests.utils import IndexMixin
from data.factories import OfficerFactory
from data.models import Officer
from alias.utils import set_aliases


class AliasUtilsTestCase(IndexMixin, TestCase):
    allow_database_queries = True

    def setUp(self):
        super(AliasUtilsTestCase, self).setUp()
        self.officer = OfficerFactory(id=1)
        self.officer_doc = OfficerInfoDocType(meta={'id': '1'})
        self.officer_doc.save()
        self.refresh_index()

    def test_set_officer_aliases(self):
        set_aliases(OfficerInfoDocType, Officer, '1', ['alias1', 'alias2'])
        expect(OfficerInfoDocType.get('1').tags).to.eq(['alias1', 'alias2'])
        expect(list(Officer.objects.get(pk=1).tags.names())).to.eq(['alias1', 'alias2'])
