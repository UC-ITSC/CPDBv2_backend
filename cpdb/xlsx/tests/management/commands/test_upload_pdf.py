import json

from django.test import TestCase, override_settings
from django.core.management import call_command

from mock import patch
from robber import expect

from data.factories import AttachmentFileFactory


class UploadPdfCommandTestCase(TestCase):
    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer_content_bucket',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_UPLOAD_PDF='uploadPdfTest'
    )
    @patch('data.models.attachment_file.aws')
    def test_upload_pdf(self, aws_mock):
        AttachmentFileFactory(
            external_id='00000105',
            source_type='PORTAL_COPA',
            url='http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf'
        )
        AttachmentFileFactory(
            external_id='123',
            source_type='DOCUMENTCLOUD',
            url='https://www.documentcloud.org/documents/2-CRID-123-CR.html'
        )
        AttachmentFileFactory(
            external_id='456',
            source_type='PORTAL_COPA_DOCUMENTCLOUD',
            url='https://www.documentcloud.org/documents/2-CRID-456-CR.html'
        )
        AttachmentFileFactory(
            external_id='789',
            source_type='SUMMARY_REPORTS_COPA_DOCUMENTCLOUD',
            url='https://www.documentcloud.org/documents/3-CRID-789-CR.html'
        )

        call_command('upload_pdf')

        expect(aws_mock.lambda_client.invoke_async.call_count).to.eq(3)
        expect(aws_mock.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdfTest',
            InvokeArgs=json.dumps({
                'url': 'https://www.documentcloud.org/documents/2-CRID-123-CR.html',
                'bucket': 'officer_content_bucket',
                'key': 'pdf/123'
            })
        )
        expect(aws_mock.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdfTest',
            InvokeArgs=json.dumps({
                'url': 'https://www.documentcloud.org/documents/2-CRID-456-CR.html',
                'bucket': 'officer_content_bucket',
                'key': 'pdf/456'
            })
        )
        expect(aws_mock.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdfTest',
            InvokeArgs=json.dumps({
                'url': 'https://www.documentcloud.org/documents/3-CRID-789-CR.html',
                'bucket': 'officer_content_bucket',
                'key': 'pdf/789'
            })
        )

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer_content_bucket',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_UPLOAD_PDF='uploadPdfTest'
    )
    @patch('data.models.attachment_file.aws')
    def test_upload_pdf_with_external_ids(self, aws_mock):
        AttachmentFileFactory(
            external_id='00000105',
            source_type='PORTAL_COPA',
            url='http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf'
        )
        AttachmentFileFactory(
            external_id='123',
            source_type='DOCUMENTCLOUD',
            url='https://www.documentcloud.org/documents/2-CRID-123-CR.html'
        )
        AttachmentFileFactory(
            external_id='456',
            source_type='PORTAL_COPA_DOCUMENTCLOUD',
            url='https://www.documentcloud.org/documents/2-CRID-456-CR.html'
        )
        AttachmentFileFactory(
            external_id='789',
            source_type='SUMMARY_REPORTS_COPA_DOCUMENTCLOUD',
            url='https://www.documentcloud.org/documents/3-CRID-789-CR.html'
        )

        call_command('upload_pdf', '00000105', '123')

        expect(aws_mock.lambda_client.invoke_async).to.be.called_once()
        expect(aws_mock.lambda_client.invoke_async).to.be.called_with(
            FunctionName='uploadPdfTest',
            InvokeArgs=json.dumps({
                'url': 'https://www.documentcloud.org/documents/2-CRID-123-CR.html',
                'bucket': 'officer_content_bucket',
                'key': 'pdf/123'
            })
        )
