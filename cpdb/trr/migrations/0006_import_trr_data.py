# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-18 08:39
from __future__ import unicode_literals
from contextlib import contextmanager
from csv import DictReader
import os
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.db import migrations, models

from azure.storage.blob import BlockBlobService


@contextmanager
def csv_from_azure(filename):
    block_blob_service = BlockBlobService(
        account_name=settings.DATA_PIPELINE_STORAGE_ACCOUNT_NAME,
        account_key=settings.DATA_PIPELINE_STORAGE_ACCOUNT_KEY
    )
    tmp_file = NamedTemporaryFile(suffix='.csv', delete=False)
    block_blob_service.get_blob_to_path('csv', filename, tmp_file.name)
    csvfile = open(tmp_file.name)
    reader = DictReader(csvfile)
    yield reader
    csvfile.close()
    os.remove(tmp_file.name)


def import_data(apps, schema_editor):
    TRR = apps.get_model('trr', 'TRR')
    blank_or_null = {
        field.get_attname(): None if field.null else ''
        for field in TRR._meta.get_fields()
        if hasattr(field, 'get_attname')
    }
    boolean_fields = [
        field.name for field in TRR._meta.get_fields()
        if type(field) in [models.fields.BooleanField, models.fields.NullBooleanField]
    ]
    boolean_map = {
        'False': False,
        'True': True
    }
    pks = []

    with csv_from_azure('20180518_trr.csv') as reader:
        for row in reader:
            for key, val in row.iteritems():
                if val == '':
                    row[key] = blank_or_null[key]
                elif key in boolean_fields:
                    row[key] = boolean_map[val]
            pk = int(row.pop('pk'))
            pks.append(pk)
            obj, created = TRR.objects.update_or_create(
                id=pk,
                defaults=row
            )

    TRR.objects.exclude(pk__in=pks).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('trr', '0005_trr_point'),
        ('data', '0037_import_policeunit_data')
    ]

    operations = [
        migrations.RunPython(
                import_data,
                reverse_code=migrations.RunPython.noop,
                elidable=True),
    ]
