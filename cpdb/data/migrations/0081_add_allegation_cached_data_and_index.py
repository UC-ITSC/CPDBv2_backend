# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-12 05:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0080_add_officer_cached_allegation_count_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='allegation',
            name='first_end_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='allegation',
            name='first_start_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='allegation',
            name='most_common_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data.AllegationCategory'),
        ),
        migrations.AddIndex(
            model_name='allegation',
            index=models.Index(fields=['crid'], name='data_allega_crid_15bee0_idx'),
        ),
    ]