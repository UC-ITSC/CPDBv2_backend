# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-15 04:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='officer',
            name='birth_year',
        ),
        migrations.RemoveField(
            model_name='officer',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='officer',
            name='last_name',
        ),
        migrations.AddField(
            model_name='officer',
            name='age_at_march_11_2016',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='officer',
            name='full_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='officerallegation',
            name='final_outcome',
            field=models.CharField(blank=True, choices=[[b'000', b'Violation Noted'], [b'001', b'1 Day Suspension'], [b'002', b'2 Day Suspension'], [b'003', b'3 Day Suspension'], [b'004', b'4 Day Suspension'], [b'005', b'5 Day Suspension'], [b'006', b'6 Day Suspension'], [b'007', b'7 Day Suspension'], [b'008', b'8 Day Suspension'], [b'009', b'9 Day Suspension'], [b'010', b'10 Day Suspension'], [b'011', b'11 Day Suspension'], [b'012', b'12 Day Suspension'], [b'013', b'13 Day Suspension'], [b'014', b'14 Day Suspension'], [b'015', b'15 Day Suspension'], [b'016', b'16 Day Suspension'], [b'017', b'17 Day Suspension'], [b'018', b'18 Day Suspension'], [b'019', b'19 Day Suspension'], [b'020', b'20 Day Suspension'], [b'021', b'21 Day Suspension'], [b'022', b'22 Day Suspension'], [b'023', b'23 Day Suspension'], [b'024', b'24 Day Suspension'], [b'025', b'25 Day Suspension'], [b'026', b'26 Day Suspension'], [b'027', b'27 Day Suspension'], [b'028', b'28 Day Suspension'], [b'029', b'29 Day Suspension'], [b'030', b'30 Day Suspension'], [b'045', b'45 Day Suspension'], [b'060', b'60 Day Suspension'], [b'090', b'90 Day Suspension'], [b'100', b'Reprimand'], [b'120', b'Suspended for 120 Days'], [b'180', b'Suspended for 180 Days'], [b'200', b'Suspended over 30 Days'], [b'300', b'Administrative Termination'], [b'400', b'Separation'], [b'500', b'Reinstated by Police Board'], [b'600', b'No Action Taken'], [b'700', b'Reinstated by Court Action'], [b'800', b'Resigned'], [b'900', b'Penalty Not Served'], [b'', b'Unknown']], max_length=3),
        ),
        migrations.AlterField(
            model_name='officerallegation',
            name='recc_outcome',
            field=models.CharField(blank=True, choices=[[b'000', b'Violation Noted'], [b'001', b'1 Day Suspension'], [b'002', b'2 Day Suspension'], [b'003', b'3 Day Suspension'], [b'004', b'4 Day Suspension'], [b'005', b'5 Day Suspension'], [b'006', b'6 Day Suspension'], [b'007', b'7 Day Suspension'], [b'008', b'8 Day Suspension'], [b'009', b'9 Day Suspension'], [b'010', b'10 Day Suspension'], [b'011', b'11 Day Suspension'], [b'012', b'12 Day Suspension'], [b'013', b'13 Day Suspension'], [b'014', b'14 Day Suspension'], [b'015', b'15 Day Suspension'], [b'016', b'16 Day Suspension'], [b'017', b'17 Day Suspension'], [b'018', b'18 Day Suspension'], [b'019', b'19 Day Suspension'], [b'020', b'20 Day Suspension'], [b'021', b'21 Day Suspension'], [b'022', b'22 Day Suspension'], [b'023', b'23 Day Suspension'], [b'024', b'24 Day Suspension'], [b'025', b'25 Day Suspension'], [b'026', b'26 Day Suspension'], [b'027', b'27 Day Suspension'], [b'028', b'28 Day Suspension'], [b'029', b'29 Day Suspension'], [b'030', b'30 Day Suspension'], [b'045', b'45 Day Suspension'], [b'060', b'60 Day Suspension'], [b'090', b'90 Day Suspension'], [b'100', b'Reprimand'], [b'120', b'Suspended for 120 Days'], [b'180', b'Suspended for 180 Days'], [b'200', b'Suspended over 30 Days'], [b'300', b'Administrative Termination'], [b'400', b'Separation'], [b'500', b'Reinstated by Police Board'], [b'600', b'No Action Taken'], [b'700', b'Reinstated by Court Action'], [b'800', b'Resigned'], [b'900', b'Penalty Not Served'], [b'', b'Unknown']], max_length=3),
        ),
    ]