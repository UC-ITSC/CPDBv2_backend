# Generated by Django 2.2.10 on 2020-05-28 03:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0122_attachmentfile_is_external_ocr'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentOCR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('page_num', models.IntegerField()),
                ('ocr_text', models.TextField(blank=True)),
                ('attachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachment_ocrs', to='data.AttachmentFile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
