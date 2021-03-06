# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-15 04:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0014_auto_20171003_0328'),
    ]

    operations = [
        migrations.AddField(
            model_name='officer',
            name='middle_initial',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='officer',
            name='suffix_name',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='officer',
            name='first_name',
            field=models.CharField(db_index=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='officer',
            name='last_name',
            field=models.CharField(db_index=True, default='', max_length=255),
            preserve_default=False,
        ),
    ]
