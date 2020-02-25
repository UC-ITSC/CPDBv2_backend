# Generated by Django 2.2.9 on 2019-12-27 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Toast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=25)),
                ('template', models.TextField(help_text='Markdown supported')),
                ('tags', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
