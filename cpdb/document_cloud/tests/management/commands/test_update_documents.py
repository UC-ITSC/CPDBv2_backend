from django.core import management
from django.test import TestCase
from mock import patch, MagicMock, call
from robber import expect

from data.factories import AllegationFactory, AttachmentFileFactory
from data.models import AttachmentFile, Allegation
from document_cloud.factories import DocumentCloudSearchQueryFactory
from document_cloud.management.commands.update_documents import Command
from document_cloud.models import DocumentCrawler


class UpdateDocumentsCommandTestCase(TestCase):
    def setUp(self):
        super(UpdateDocumentsCommandTestCase, self).setUp()

    def tearDown(self):
        AttachmentFile.objects.all().delete()
        Allegation.objects.all().delete()

    def test_get_search_syntaxes(self):
        queries = DocumentCloudSearchQueryFactory.create_batch(2)

        with patch('document_cloud.management.commands.update_documents.DocumentCloud') as mock_documentcloud:
            mock_search = mock_documentcloud().documents.search

            management.call_command('update_documents')

            expect(mock_search.call_args_list).to.eq([
                call(queries[0].query),
                call(queries[1].query)
            ])

    def test_get_call_process_documentcloud_result(self):
        query = DocumentCloudSearchQueryFactory()

        with patch('document_cloud.management.commands.update_documents.DocumentCloud') as mock_documentcloud:
            with patch(
                'document_cloud.management.commands.update_documents.Command.process_documentcloud_result'
            ) as mock_process:
                cleaned_result = MagicMock(title='title')
                mock_search = mock_documentcloud().documents.search
                mock_search.return_value = [cleaned_result]

                management.call_command('update_documents')

                mock_process.assert_called_with(cleaned_result, query.type)

    def test_skip_empty_syntaxes(self):
        queries = [
            DocumentCloudSearchQueryFactory(),
            DocumentCloudSearchQueryFactory(query='')
        ]

        with patch('document_cloud.management.commands.update_documents.DocumentCloud') as mock_documentcloud:
            mock_search = mock_documentcloud().documents.search

            management.call_command('update_documents')

            mock_search.assert_called_once_with(queries[0].query)

    def test_create_crawler_log(self):
        expect(DocumentCrawler.objects.all().count()).to.eq(0)

        management.call_command('update_documents')

        expect(DocumentCrawler.objects.all().count()).to.eq(1)

    def test_clean_results_remove_duplicate(self):
        command = Command()
        raw_results = [
            MagicMock(title='abc'),
            MagicMock(title='abc')
        ]

        results = command.clean_documentcloud_results(raw_results)

        expect(results).to.eq(raw_results[:1])

    def test_process_no_crid(self):
        command = Command()
        AttachmentFileFactory(title='old')

        with patch('document_cloud.management.commands.update_documents.DocumentcloudService') as mock_service:
            mock_service().parse_crid_from_title = MagicMock(return_value=None)

            command.process_documentcloud_result(MagicMock(title='new'), 'CR')

            expect(AttachmentFile.objects.all().count()).to.eq(1)
            expect(AttachmentFile.objects.all()[0].title).to.eq('old')

    def test_update_title_if_title_changed(self):
        command = Command()
        allegation = AllegationFactory()
        AttachmentFileFactory(title='old', allegation=allegation, url='url id')

        with patch('document_cloud.management.commands.update_documents.DocumentcloudService') as mock_service:
            mock_service().parse_crid_from_title = MagicMock(return_value=allegation.crid)

            command.process_documentcloud_result(MagicMock(title='new', id='id'), 'CR')

            expect(AttachmentFile.objects.all().count()).to.eq(1)
            expect(AttachmentFile.objects.all()[0].title).to.eq('new')

    def test_insert_new_document_if_allegation_existed(self):
        command = Command()
        allegation = AllegationFactory()

        with patch('document_cloud.management.commands.update_documents.DocumentcloudService') as mock_service_class:
            mock_service = mock_service_class()
            mock_service.parse_crid_from_title = MagicMock(return_value=allegation.crid)
            mock_service.parse_link = MagicMock(return_value={})

            expect(AttachmentFile.objects.all().count()).to.eq(0)

            command.process_documentcloud_result(
                MagicMock(title='new', id=1, canonical_url='canonical_url'), 'CR'
            )

            expect(AttachmentFile.objects.all().count()).to.eq(1)
            media = AttachmentFile.objects.all()[0]
            expect(media.title).to.eq('new')
            expect(media.allegation.id).to.eq(allegation.id)

    def test_not_process_if_allegation_not_existed(self):
        command = Command()

        with patch('document_cloud.management.commands.update_documents.DocumentcloudService') as mock_service_class:
            mock_service = mock_service_class()
            mock_service.parse_crid_from_title = MagicMock(return_value='1')
            mock_service.parse_link = MagicMock(return_value={})

            expect(AttachmentFile.objects.all().count()).to.eq(0)

            command.process_documentcloud_result(MagicMock(title='new'), 'CR')

            expect(AttachmentFile.objects.all().count()).to.eq(0)

    def test_replace_hyphen_with_space(self):
        command = Command()
        allegation = AllegationFactory()

        with patch('document_cloud.management.commands.update_documents.DocumentcloudService') as mock_service_class:
            mock_service = mock_service_class()
            mock_service.parse_crid_from_title = MagicMock(return_value=allegation.crid)
            mock_service.parse_link = MagicMock(return_value={})

            command.process_documentcloud_result(
                MagicMock(title='new-document', id=allegation.id, canonical_url='canonical_url 1'), 'CR'
            )
            command.process_documentcloud_result(
                MagicMock(title='new - document', id=allegation.id, canonical_url='canonical_url 2'), 'CR'
            )

            media = AttachmentFile.objects.first()
            expect(media.title).to.eq('new document')
            expect(media.allegation.id).to.eq(allegation.id)

            media = AttachmentFile.objects.all()[1]
            expect(media.title).to.eq('new - document')
            expect(media.allegation.id).to.eq(allegation.id)