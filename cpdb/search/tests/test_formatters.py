from mock import Mock

from django.test import SimpleTestCase

from robber import expect

from search.formatters import (
    SimpleFormatter, OfficerFormatter, NameFormatter, OfficerV2Formatter,
    NameV2Formatter, FAQFormatter, ReportFormatter, Formatter, UnitFormatter, CrFormatter
)


class FormatterTestCase(SimpleTestCase):
    def test_format(self):
        expect(Formatter().format).to.throw(NotImplementedError)


class SimpleFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value='a'))

        expect(
            SimpleFormatter().doc_format(doc)
        ).to.be.equal('a')

    def test_format(self):
        doc1 = Mock(
            to_dict=Mock(return_value={'a': 'a'}),
            _id='a_id'
        )
        doc2 = Mock(
            to_dict=Mock(return_value={'b': 'b'}),
            _id='b_id'
        )
        response = Mock(hits=[doc1, doc2])

        expect(
            SimpleFormatter().format(response)
        ).to.be.eq([{'a': 'a', 'id': 'a_id'}, {'b': 'b', 'id': 'b_id'}])

    def test_serialize(self):
        doc = Mock(
            to_dict=Mock(return_value={'a': 'a'}),
            _id='a_id'
        )
        expect(SimpleFormatter().serialize([doc])).to.eq([{
            'a': 'a',
            'id': 'a_id'
        }])


class OfficerFormatterTestCase(SimpleTestCase):
    def test_officer_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'full_name': 'name',
            'badge': '123',
            'to': 'to',
            'tags': ['tag1', 'tag2'],
            'allegation_count': 10,
            'sustained_count': 2,
            'visual_token_background_color': '#ffffff',
            'unit': '001',
            'rank': 'some rank',
            'birth_year': 1972,
            'race': 'White',
            'sex': 'Male'
        }))

        expect(
            OfficerFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'result_extra_information': 'Badge # 123',
                'to': 'to',
                'result_reason': 'tag1, tag2',
                'tags': ['tag1', 'tag2'],
                'visual_token_background_color': '#ffffff',
                'unit': '001',
                'rank': 'some rank',
                'allegation_count': 10,
                'sustained_count': 2,
                'race': 'White',
                'birth_year': 1972,
                'sex': 'Male',
                'salary': None  # no data yet so always return None here
            }
        })

    def test_unit_officer_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'full_name': 'name',
            'badge': '123',
            'to': 'to',
            'tags': ['tag1', 'tag2'],
            'visual_token_background_color': '#ffffff',
            'unit': '001',
            'allegation_count': 10,
            'sustained_count': 2,
            'unit_description': 'foo bar',
            'rank': 'some rank',
            'birth_year': 1972,
            'race': 'White',
            'sex': 'Male'
        }))

        expect(
            OfficerFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'result_extra_information': 'foo bar',
                'to': 'to',
                'result_reason': 'tag1, tag2',
                'tags': ['tag1', 'tag2'],
                'visual_token_background_color': '#ffffff',
                'unit': '001',
                'allegation_count': 10,
                'sustained_count': 2,
                'rank': 'some rank',
                'birth_year': 1972,
                'race': 'White',
                'sex': 'Male',
                'salary': None  # no data yet so always return None here
            }
        })


class UnitFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock()
        doc.to_dict = Mock(return_value={
            'name': '123',
            'description': 'foo bar',
            'to': '/unit/123/',
            'tags': ['foo']
        })

        expect(
            UnitFormatter().doc_format(doc)
        ).to.be.eq({
            'text': '123',
            'payload': {
                'result_text': 'foo bar',
                'result_extra_information': '123',
                'to': '/unit/123/',
                'tags': ['foo']
            }
        })

    def test_doc_format_without_tags(self):
        doc = Mock()
        doc.to_dict = Mock(return_value={
            'name': '123',
            'description': 'foo bar',
            'to': '/unit/123/'
        })

        expect(
            UnitFormatter().doc_format(doc)
        ).to.be.eq({
            'text': '123',
            'payload': {
                'result_text': 'foo bar',
                'result_extra_information': '123',
                'to': '/unit/123/',
                'tags': []
            }
        })


class NameFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'url': 'url',
            'tags': ['t1', 't2'],
            'name': 'name'
        }))

        expect(
            NameFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'url': 'url',
                'tags': ['t1', 't2']
            },
        })


class OfficerV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'full_name': 'name',
            'tags': ['t1', 't2'],
            'badge': '123',
            'to': 'to'
        }))

        expect(
            OfficerV2Formatter().doc_format(doc)
        ).to.be.eq({
            'result_text': 'name',
            'result_extra_information': 'Badge # 123',
            'to': 'to',
            'tags': ['t1', 't2']
        })


class NameV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'url': 'url',
            'tags': ['t1', 't2'],
            'name': 'name'
        }))

        expect(
            NameV2Formatter().doc_format(doc)
        ).to.be.eq({
            'result_text': 'name',
            'url': 'url',
            'tags': ['t1', 't2']
        })


class FAQFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(question='question', answer='answer', tags=['t1', 't2'])

        expect(
            FAQFormatter().doc_format(doc)
        ).to.be.eq({
            'question': 'question',
            'answer': 'answer',
            'tags': ['t1', 't2']
        })


class ReportFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(
            publication='publication',
            author='author',
            title='title',
            excerpt='excerpt',
            tags=['t1', 't2']
        )

        expect(
            ReportFormatter().doc_format(doc)
        ).to.be.eq({
            'publication': 'publication',
            'author': 'author',
            'title': 'title',
            'excerpt': 'excerpt',
            'tags': ['t1', 't2']
        })


class CrFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'crid': '123456',
            'to': '/complaint/123456/'
        }))

        expect(
            CrFormatter().doc_format(doc)
        ).to.eq({
            'text': '123456',
            'payload': {
                'result_text': '123456',
                'to': '/complaint/123456/',
            },
        })
