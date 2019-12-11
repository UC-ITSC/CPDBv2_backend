from django.conf import settings
from datetime import datetime
import pytz

from data.models import AttachmentFile
from document_cloud.constants import DOCUMENT_CRAWLER_SUCCESS, DOCUMENT_CRAWLER_FAILED
from document_cloud.models import DocumentCrawler
from shared.aws import aws


class BaseAttachmentImporter(object):
    source_type = None
    all_source_types = None

    def __init__(self, logger):
        self.log_data = []
        self.error_data = []
        self.logger = logger
        self.new_attachments = []
        self.num_updated_attachments = 0
        self.crawler_name = self.source_type.lower() if self.source_type else None
        self.current_step = None

    def log_info(self, message):
        self.logger.info(message)
        self.log_data.append(message)

    def log_error(self, error):
        self.logger.info(error)
        self.error_data.append(error)

    def generate_s3_file(self, filename, data):
        timestamps = datetime.now(pytz.utc).strftime(format='%Y-%m-%d-%H%M%S')
        s3_key = f'{self.crawler_name}/{filename}-{timestamps}.txt'

        aws.s3.put_object(
            Body=data.encode(),
            Bucket=settings.S3_BUCKET_CRAWLER_LOG,
            Key=s3_key,
            ContentType='text/plain'
        )
        return s3_key

    def generate_s3_log_file(self):
        filename = self.crawler_name.replace("_", "-")
        data = '\n'.join(self.log_data)

        return self.generate_s3_file(filename, data)

    def generate_s3_error_log_file(self):
        filename = f'error-traceback-log-{self.crawler_name.replace("_", "-")}'
        data = '\n'.join(self.error_data)

        return self.generate_s3_file(filename, data)

    def get_current_num_successful_run(self):
        return DocumentCrawler.objects.filter(source_type=self.source_type, status='Success').count()

    def set_current_step(self, step):
        step_length = len(step)
        left_space = int(round(80 - step_length)/2)
        right_space = 80 - step_length - left_space
        self.current_step = step
        self.log_info('')
        self.log_info(f'{"="*left_space} {self.current_step} {"="*right_space}')

    def record_crawler_result(self, status, message):
        num_documents = AttachmentFile.objects.filter(
            source_type__in=self.all_source_types
        ).count()
        num_new_attachments = len(self.new_attachments)
        num_successful_run = self.get_current_num_successful_run()

        self.log_info(f'Creating {num_new_attachments} attachments')
        self.log_info(f'Updating {self.num_updated_attachments} attachments')
        self.log_info(f'Current Total {self.crawler_name} attachments: {num_documents}')
        self.log_info(message)

        if status == DOCUMENT_CRAWLER_SUCCESS:
            num_successful_run += 1

        log_key = self.generate_s3_log_file()
        error_key = self.generate_s3_error_log_file() if self.error_data else None

        DocumentCrawler.objects.create(
            source_type=self.source_type,
            status=status,
            num_documents=num_documents,
            num_new_documents=num_new_attachments,
            num_updated_documents=self.num_updated_attachments,
            num_successful_run=num_successful_run,
            log_key=log_key,
            error_key=error_key,
        )

    def record_success_crawler_result(self):
        self.record_crawler_result(DOCUMENT_CRAWLER_SUCCESS, 'Done importing!')

    def record_failed_crawler_result(self):
        self.record_crawler_result(DOCUMENT_CRAWLER_FAILED, f'ERROR: Error occurred while {self.current_step}!')
