from __future__ import unicode_literals

from django.db import models
from datetime import datetime, date

# Create your models here.

class Report(models.Model):
    ip = models.CharField('pvs ip address', max_length=20,default='')
    local_ip = models.CharField('pvs local ip address', max_length=20,null=True)
    hardware = models.CharField('pi hardware', max_length=20,default='')
    revision = models.CharField('pi revision', max_length=20,default='')
    serial = models.CharField('pi serial', max_length=20,default='')
    dbconfig = models.TextField('pvs dbconfig', default='{}')
    last_update_time = models.DateTimeField('last update time',default=datetime.now)

class DbConfig(models.Model):
    serial = models.CharField('pi serial', max_length=20)
    dbconfig = models.TextField('pvs dbconfig', default='{}')
    create_time = models.DateTimeField('created time', default=datetime.now)
    pvs_update_time = models.DateTimeField('pvs update time', null=True)
    pvs_updated = models.BooleanField('pvs update acked', default=False)
    
class Energy(models.Model):
    
    TYPE_ENERGY_DC_LIFE = 'en_dc_life'
    TYPE_ENERGY_TODAY = 'en_today'
    TYPE_AC_OUTPUT_VOLTAGE = 'ac_v'
    TYPE_AC_OUTPUT_CURRENT = 'ac_c'
    TYPE_AC_OUTPUT_WATT = 'ac_w'
    ENERGY_TYPE_CHOICES = (
        (TYPE_ENERGY_DC_LIFE,'Energy Output DC Life'),
        (TYPE_ENERGY_TODAY, 'Energy Output Today'),
        (TYPE_AC_OUTPUT_VOLTAGE, 'AC Output Voltage'),
        (TYPE_AC_OUTPUT_CURRENT, 'AC Output Current'),
        (TYPE_AC_OUTPUT_WATT, 'AC Output Watt'))
    
    TYPE_MEASURE_INDEX_DC1 = 'dc1'
    TYPE_MEASURE_INDEX_DC2 = 'dc2'
    TYPE_MEASURE_INDEX_DC3 = 'dc3'
    MEASURE_INDEX_CHOICES = (
        (TYPE_MEASURE_INDEX_DC1,'dc1'),
        (TYPE_MEASURE_INDEX_DC2,'dc2'),
        (TYPE_MEASURE_INDEX_DC3,'dc3'),
        )
    
    serial = models.CharField('pi serial', max_length=20)
    data_id = models.IntegerField('rowdata id in pvs',null=True)
    create_time = models.DateTimeField('pvi energy read time')
    pvi_name = models.CharField('pvi name in pvs', max_length=50, null=True)
    modbus_id = models.IntegerField('modbus id the value from')
    value = models.IntegerField('pvi energy value')
    type = models.CharField('energy value type',max_length=20,choices=ENERGY_TYPE_CHOICES)
    measurement_index = models.CharField('pvi measurement index',max_length=10,
                                     choices=MEASURE_INDEX_CHOICES,null=True,
                                     default=TYPE_MEASURE_INDEX_DC1)
    
class Weather(models.Model):    
    serial = models.CharField('pi serial', max_length=20)
    create_time = models.DateTimeField('pvs environment weather read time')
    temperature = models.FloatField('temperature value at site',null=True)
    uv = models.IntegerField('UV index at site',null=True)
    visibility = models.FloatField('visibility Index at site',null=True)
    
    