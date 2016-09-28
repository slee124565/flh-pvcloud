# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-28 15:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pvs', '0005_auto_20160928_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='energy',
            name='create_time',
            field=models.DateTimeField(null=True, verbose_name='pvi energy read time'),
        ),
        migrations.AlterField(
            model_name='energy',
            name='modbus_id',
            field=models.IntegerField(null=True, verbose_name='modbus id the value from'),
        ),
        migrations.AlterField(
            model_name='energy',
            name='type',
            field=models.CharField(choices=[('en_dc_life', 'Energy Output DC Life'), ('en_today', 'Energy Output Today'), ('ac_v', 'AC Output Voltage'), ('ac_c', 'AC Output Current'), ('ac_w', 'AC Output Watt')], max_length=20, null=True, verbose_name='energy value type'),
        ),
        migrations.AlterField(
            model_name='energy',
            name='value',
            field=models.IntegerField(null=True, verbose_name='pvi energy value'),
        ),
    ]