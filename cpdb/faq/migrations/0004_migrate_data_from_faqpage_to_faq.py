# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-30 03:33
from __future__ import unicode_literals

from django.db import migrations

from tqdm import tqdm


def copy_data_from_faqpage_to_faq(apps, schema_editor):
    FAQ = apps.get_model('faq', 'FAQ')
    FAQPage = apps.get_model('faq', 'FAQPage')
    for faq_page in tqdm(FAQPage.objects.all(), desc='Create faqs'):
        FAQ.objects.create(
            title=faq_page.title,
            body=faq_page.body)


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0003_add_faq_model'),
    ]

    operations = [
        migrations.RunPython(copy_data_from_faqpage_to_faq),
    ]
