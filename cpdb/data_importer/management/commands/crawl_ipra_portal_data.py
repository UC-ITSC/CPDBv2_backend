import logging

from django.core.management import BaseCommand
from django.conf import settings

from documentcloud import DocumentCloud
from tqdm import tqdm

from data_importer.ipra_portal_crawler import crawl_and_update_attachments
from email_service.service import send_cr_attachment_available_email
from document_cloud.constants import AUTO_UPLOAD_DESCRIPTION
from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from document_cloud.utils import parse_id, parse_link, get_url, format_copa_documentcloud_title

logger = logging.getLogger('crawler.crawl_ipra_portal_data')


def upload_copa_documents():
    client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

    attachments = AttachmentFile.objects.filter(source_type=AttachmentSourceType.COPA, file_type=MEDIA_TYPE_DOCUMENT)

    logger.info(f'Uploading {len(attachments)} documents to DocumentCloud')

    for attachment in tqdm(attachments):
        cloud_document = client.documents.upload(
            attachment.original_url,
            title=format_copa_documentcloud_title(attachment.allegation.crid, attachment.title),
            description=AUTO_UPLOAD_DESCRIPTION,
            access='public',
            force_ocr=True
        )

        attachment.external_id = parse_id(cloud_document.id)
        attachment.source_type = AttachmentSourceType.COPA_DOCUMENTCLOUD
        attachment.title = cloud_document.title
        attachment.url = get_url(cloud_document)
        attachment.tag = 'CR'
        attachment.additional_info = parse_link(cloud_document.canonical_url)
        attachment.preview_image_url = cloud_document.normal_image_url
        attachment.external_last_updated = cloud_document.updated_at
        attachment.external_created_at = cloud_document.created_at
        attachment.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_attachments = crawl_and_update_attachments(logger)
        upload_copa_documents()
        send_cr_attachment_available_email(new_attachments)
