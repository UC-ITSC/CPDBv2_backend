# Generated by Django 2.1.3 on 2019-01-08 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0098_rename_allegation_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachmentfile',
            name='allegation',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='attachmentrequest',
            name='allegation',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='complainant',
            name='allegation',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='investigatorallegation',
            name='allegation',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='involvement',
            name='allegation',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='officerallegation',
            name='allegation',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='policewitness',
            name='allegation',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='victim',
            name='allegation',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
