from datetime import datetime

from django.test.testcases import TestCase

import pytz
from mock import patch
from robber import expect

from document_cloud.models import DocumentCrawler
from data.factories import AllegationCategoryFactory, AllegationFactory, AttachmentFileFactory
from data.models import Allegation, AttachmentFile
from data_importer.ipra_portal_crawler.service import AutoOpenIPRA
from data.constants import AttachmentSourceType


class AutoOpenIPRATest(TestCase):
    def test_parse_incidents(self):
        incidents = [{
            'attachments': [
                {
                    'type': 'Audio',
                    'link': 'http://audio_link',
                    'title': 'Audio Clip',
                    'last_updated': '2018-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '1',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject1', 'Unknown'],
        }]
        expect(AutoOpenIPRA.parse_incidents(incidents)).to.be.eq([{
            'allegation': {
                'crid': '1',
                'incident_date': datetime(2013, 4, 30, 21, 30),
                'attachment_files': [{
                    'file_type': 'audio',
                    'title': 'Audio Clip',
                    'url': 'http://audio_link',
                    'original_url': 'http://audio_link',
                    'tag': 'Audio',
                    'source_type': 'COPA',
                    'external_last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
                }],
                'subjects': ['Subject1', 'Unknown']
            },
            'allegation_category': {
                'category': 'Incident',
                'allegation_name': 'Allegation Name'
            },
            'police_shooting': True
        }])

    @patch('data_importer.ipra_portal_crawler.service.OpenIpraInvestigationCrawler')
    @patch('data_importer.ipra_portal_crawler.service.ComplaintCrawler')
    def test_crawl_open_ipra(self, complaint_crawler, link_crawler):
        link_crawler.return_value.crawl.return_value = ['link 1']
        complaint_crawler.return_value.crawl.return_value = 'something'
        expect(AutoOpenIPRA.crawl_open_ipra()).to.be.eq(['something'])

    @patch('data_importer.ipra_portal_crawler.service.AutoOpenIPRA.crawl_open_ipra')
    def test_import_new(self, open_ipra):
        open_ipra.return_value = [{
            'attachments': [
                {
                    'type': 'Audio',
                    'link': 'http://audio_link',
                    'title': 'Audio Clip',
                    'last_updated': '2018-10-30T15:00:03+00:00'
                },
                {
                    'type': 'Document',
                    'link': 'http://document_link',
                    'title': 'Audio Clip',
                    'last_updated': '2017-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '123',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject', '', 'Unknown'],
        }, {
            'attachments': [
                {
                    'type': 'Document',
                    'link': 'http://pdf_link',
                    'title': 'Audio Clip',
                    'last_updated': '2017-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '456',
            'time': '04-30-2013 9:30 pm',
            'subjects': ['Subject 2'],
        }]
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        allegation = AllegationFactory(crid='123')
        attachment_file = AttachmentFileFactory(
            allegation=allegation,
            source_type='',
            external_id='http://document_link',
            original_url='http://document_link')
        expect(DocumentCrawler.objects.count()).to.eq(0)
        expect(Allegation.objects.count()).to.eq(1)
        expect(Allegation.objects.get(crid='123').attachment_files.count()).to.eq(1)

        AutoOpenIPRA.import_new()

        expect(Allegation.objects.count()).to.eq(1)
        expect(Allegation.objects.get(crid='123').subjects).to.eq(['Subject'])
        expect(AttachmentFile.objects.filter(allegation=allegation).count()).to.eq(2)
        expect(AttachmentFile.objects.get(pk=attachment_file.pk).source_type).to.eq(AttachmentSourceType.COPA)

        expect(DocumentCrawler.objects.count()).to.eq(1)
        crawler_log = DocumentCrawler.objects.first()
        expect(crawler_log.source_type).to.eq(AttachmentSourceType.COPA)
        expect(crawler_log.num_documents).to.eq(2)
        expect(crawler_log.num_new_documents).to.eq(1)
        expect(crawler_log.num_updated_documents).to.eq(1)

    @patch('data_importer.ipra_portal_crawler.service.AutoOpenIPRA.crawl_open_ipra')
    def test_update(self, open_ipra):
        open_ipra.return_value = [{
            'attachments': [
                {
                    'type': 'Document',
                    'link': 'http://document_link',
                    'title': 'pdf file',
                    'last_updated': '2018-10-30T15:00:03+00:00'
                }
            ],
            'date': '04-30-2013',
            'log_number': '123',
            'time': '04-30-2013 9:30 pm',
            'type': 'Allegation Name',
            'subjects': ['Subject', '', 'Unknown'],
        }]
        AllegationCategoryFactory(category='Incident', allegation_name='Allegation Name')
        attachment_file = AttachmentFileFactory(
            allegation__crid='123',
            title='old_title',
            source_type=AttachmentSourceType.COPA,
            external_id='http://document_link',
            original_url='http://document_link')

        AutoOpenIPRA.import_new()

        expect(AttachmentFile.objects.get(pk=attachment_file.pk).title).to.eq('pdf file')
