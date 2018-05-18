# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-10 09:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0034_area_extra_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='police_hq',
            field=models.ForeignKey(help_text=b'This beat contains police-district HQ', null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Area'),
        ),
    ]