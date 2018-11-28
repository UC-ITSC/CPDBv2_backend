# Generated by Django 2.1.3 on 2018-11-23 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_terms', '0011_drop_link_scheme_and_host'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchtermitem',
            name='call_to_action_type',
            field=models.CharField(choices=[('view_all', 'View All'), ('plain_text', 'Plain text'), ('link', 'Link')], default='plain_text', max_length=20),
        ),
    ]
