# Generated by Django 2.1.3 on 2018-12-17 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[['cr_available', 'CR attachment available'], ['cr_request', 'CR attachment request'], ['trr_available', 'TRR attachment available'], ['trr_request', 'TRR attachment request']], max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('from_email', models.EmailField(max_length=255)),
            ],
        ),
    ]
