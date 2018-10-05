# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-10-03 03:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity_grid', '0004_activitypaircard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitypaircard',
            name='officer1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_pair_card1', to='data.Officer'),
        ),
        migrations.AlterField(
            model_name='activitypaircard',
            name='officer2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_pair_card2', to='data.Officer'),
        ),
    ]