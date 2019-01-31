# Generated by Django 2.1.3 on 2019-01-08 02:29

from django.db import migrations
from django.db.models import Subquery, OuterRef

from tqdm import tqdm


def populate_new_allegation_field(apps, schema_editor):
    Allegation = apps.get_model('data', 'Allegation')
    model_classes = [
        apps.get_model('data', 'Victim'),
        apps.get_model('data', 'PoliceWitness'),
        apps.get_model('data', 'OfficerAllegation'),
        apps.get_model('data', 'Involvement'),
        apps.get_model('data', 'InvestigatorAllegation'),
        apps.get_model('data', 'Complainant'),
        apps.get_model('data', 'AttachmentRequest'),
        apps.get_model('data', 'AttachmentFile'),
    ]

    for model_class in tqdm(model_classes, desc='updating new allegation field'):
        try:
            objects = model_class.objects
        except AttributeError:
            objects = model_class.bulk_objects

        objects.filter(allegation_old_fk__isnull=False).update(
            allegation=Subquery(Allegation.objects.filter(id=OuterRef('allegation_old_fk_id')).values('crid')[:1])
        )


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0099_add_new_allegation_fk'),
    ]

    operations = [
        migrations.RunPython(
                populate_new_allegation_field,
                reverse_code=migrations.RunPython.noop,
                elidable=True),
    ]
