# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-11-02 03:21
from __future__ import unicode_literals

from django.db import migrations


def set_source_type(apps, schema_editor):
    AttachmentFile = apps.get_model('data', 'AttachmentFile')
    AttachmentFile.objects.filter(source_type='COPA').update(source_type='PORTAL_COPA')
    AttachmentFile.objects.filter(source_type='COPA_DOCUMENTCLOUD').update(source_type='PORTAL_COPA_DOCUMENTCLOUD')


class Migration(migrations.Migration):
    dependencies = [
        ('data', '0112_attachmentfile_show'),
    ]

    operations = [
        migrations.RunPython(set_source_type)
    ]