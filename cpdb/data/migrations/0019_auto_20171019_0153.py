# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-19 06:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0018_victim'),
    ]

    operations = [
        migrations.AlterField(
            model_name='award',
            name='tracking_no',
            field=models.CharField(max_length=255, null=True),
        ),
    ]