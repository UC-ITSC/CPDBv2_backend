# Generated by Django 2.2.9 on 2020-02-12 08:53

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('activity_log', '0001_add_activity_log_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTagsAnalyze',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='activitylog',
            name='action_type',
            field=models.CharField(choices=[('ADD_TAG_TO_DOCUMENT', 'Add tag to document'), ('REMOVE_TAG_FROM_DOCUMENT', 'Remove tag from document')], max_length=255),
        ),
    ]
