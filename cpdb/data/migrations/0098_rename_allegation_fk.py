# Generated by Django 2.1.3 on 2019-01-08 03:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0097_merge_20190101_2250'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='allegation',
            name='data_allega_crid_15bee0_idx',
        ),
        migrations.RenameField(
            model_name='attachmentfile',
            old_name='allegation',
            new_name='allegation_old_fk',
        ),
        migrations.RenameField(
            model_name='attachmentrequest',
            old_name='allegation',
            new_name='allegation_old_fk',
        ),
        migrations.RenameField(
            model_name='complainant',
            old_name='allegation',
            new_name='allegation_old_fk',
        ),
        migrations.RenameField(
            model_name='investigatorallegation',
            old_name='allegation',
            new_name='allegation_old_fk',
        ),
        migrations.RenameField(
            model_name='involvement',
            old_name='allegation',
            new_name='allegation_old_fk',
        ),
        migrations.RenameField(
            model_name='officerallegation',
            old_name='allegation',
            new_name='allegation_old_fk',
        ),
        migrations.RenameField(
            model_name='policewitness',
            old_name='allegation',
            new_name='allegation_old_fk',
        ),
        migrations.RenameField(
            model_name='victim',
            old_name='allegation',
            new_name='allegation_old_fk',
        ),
        migrations.AlterUniqueTogether(
            name='attachmentfile',
            unique_together={('allegation_old_fk', 'external_id', 'source_type')},
        ),
        migrations.AlterUniqueTogether(
            name='attachmentrequest',
            unique_together={('allegation_old_fk', 'email')},
        ),
    ]
