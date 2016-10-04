from __future__ import unicode_literals

from django.db import models
from django.db.models import Count, Max
from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)
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
    TYPE_VOLTAGE = 'voltage'
    TYPE_CURRENT = 'current'
    TYPE_WATTAGE = 'wattage'
    ENERGY_TYPE_CHOICES = (
        (TYPE_ENERGY_DC_LIFE,'Energy Output DC Life'),
        (TYPE_ENERGY_TODAY, 'Energy Output Today'),
        (TYPE_VOLTAGE, 'Voltage'),
        (TYPE_CURRENT, 'Current'),
        (TYPE_WATTAGE, 'Wattage'))
    
    TYPE_MEASURE_INDEX_GRID = 'grid'
    TYPE_MEASURE_INDEX_DC1 = 'dc1'
    TYPE_MEASURE_INDEX_DC2 = 'dc2'
    TYPE_MEASURE_INDEX_DC3 = 'dc3'
    MEASURE_INDEX_CHOICES = (
        (TYPE_MEASURE_INDEX_DC1,'grid'),
        (TYPE_MEASURE_INDEX_DC1,'dc1'),
        (TYPE_MEASURE_INDEX_DC2,'dc2'),
        (TYPE_MEASURE_INDEX_DC3,'dc3'),
        )
    
    serial = models.CharField('pi serial', max_length=20)
    data_id = models.IntegerField('rowdata id in pvs',null=True)
    create_time = models.DateTimeField('pvi energy read time',null=True)
    pvi_name = models.CharField('pvi name in pvs', max_length=50, null=True)
    modbus_id = models.IntegerField('modbus id the value from',null=True)
    value = models.IntegerField('pvi energy value',null=True)
    type = models.CharField('energy value type',max_length=20,choices=ENERGY_TYPE_CHOICES,null=True)
    measurement_index = models.CharField('pvi measurement index',max_length=10,
                                     choices=MEASURE_INDEX_CHOICES,null=True,
                                     default=TYPE_MEASURE_INDEX_DC1)
    
    @classmethod
    def get_distinct_serial(cls):
        '''return a list of distinct pvs serial'''
        #return Energy.objects.distinct('serial').values_list('serial',flat=True).order_by('serial')
        return list(Energy.objects.values('serial').annotate(Count('serial')).values_list('serial',flat=True))
    
    @classmethod
    def get_calculated_energy_hourly_output(cls,pvs_serial=None,date_since=None):
        '''return a json data of pvs energy hourly output value for specific pvs serial, 
        if pvs_serial is None, it will return all pvs energy hourly output json data
        ::
            [
                {'date': 'YYYY-mm-dd HH:00:00', 
                '<modbus_id>': xx, '<modbus_id>': xx, ...},
                ...
            ]
        '''
        energy_list = cls.get_energy_daily_output_by_hour(pvs_serial, date_since)
        for p_serial in energy_list:
            pvs_en_data = energy_list[p_serial]
            en_date_str_list = pvs_en_data.keys()
            en_date_str_list.sort()
            en_date_str_list.reverse()
            logger.debug('sorted en_date_str_list:\n%s' % str(en_date_str_list))
            if len(en_date_str_list) < 2:
                logger.warning('energy sample data not enough, return empty dict')
                energy_list[p_serial] = {}
            else:
                for p_count in range(len(en_date_str_list)-1):
                    p_hour = en_date_str_list[p_count]
                    p_hour_pre = en_date_str_list[p_count+1]
                    p_hour_en_data = pvs_en_data[p_hour]
                    p_hour_pre_en_data = pvs_en_data[p_hour_pre]
                    for p_key in p_hour_en_data:
                        if p_key != 'date':
                            logger.debug('%s - %s' % (str(p_hour_en_data),str(p_hour_pre_en_data)))
                            # same date calculate
                            if p_hour[:10] == p_hour_pre[:10]:
                                if (p_hour_en_data.get(p_key) < p_hour_pre_en_data.get(p_key,0)):
                                    logger.warning('energy value conflict (%s,%s), set zero' % (
                                                                p_hour_en_data,
                                                                p_hour_pre_en_data))
                                    p_hour_en_data[p_key] = 0
                                else:
                                    p_hour_en_data[p_key] = (p_hour_en_data.get(p_key) - 
                                                                p_hour_pre_en_data.get(p_key,0))
                            else:
                                logger.debug('date changed, set value 0')
                                p_hour_en_data[p_key] = 0
                            logger.debug('result: %s' % str(p_hour_en_data))
                logger.debug('remove energy entry %s' % pvs_en_data[en_date_str_list[-1]]) 
                del pvs_en_data[en_date_str_list[-1]]
        return energy_list
        
    @classmethod
    def get_energy_daily_output_by_hour(cls,pvs_serial=None,date_since=None):    
        '''return a json data of pvs energy hourly output value for specific pvs serial, 
        if pvs_serial is None, it will return all pvs energy hourly output json data
        ::
            [
                {'date': 'YYYY-mm-dd HH:00:00', 
                '<modbus_id>': xx, '<modbus_id>': xx, ...},
                ...
            ]
        '''
        DEFAULT_DAY_SINCE = 3
        pvs_serial_list = cls.get_distinct_serial()
        serial_list = []
        if pvs_serial is None:
            serial_list = pvs_serial_list
            logger.debug('param pvs_serial is None, set to all pvs serial')
        else:
            if not pvs_serial in pvs_serial_list:
                logger.warning('error pvs_serial %s param, not exist in db' % pvs_serial)
                return None
            else:
                logger.debug('param pvs_serial = %s' % str(pvs_serial))
                serial_list.append(pvs_serial)
    
        if date_since is None:
            date_since = (datetime.today() + timedelta(days=-DEFAULT_DAY_SINCE))
        logger.debug('param date_since = %s' % str(date_since))

        queryset = Energy.objects.filter(type='en_today',
                                         create_time__gte=date_since
                                ).extra({'en_day':"date(create_time)",
                                         'en_hour':'hour(create_time)'}
                                ).values('serial','modbus_id','en_day','en_hour'
                                ).annotate(max_value=Max('value'
                                )).order_by('en_day','en_hour')
        if not pvs_serial is None:
            queryset = queryset.filter(serial=pvs_serial)
        
        energy_list = {}
        for entry in serial_list:
            energy_list[entry] = {}
            
        for entry in queryset:
            en_day_str = '%s %02d:00:00' % ( entry.get('en_day').strftime('%Y-%m-%d'),
                                     entry.get('en_hour'))
            en_day = energy_list[entry.get('serial')].get(en_day_str,None)
            if en_day is None:
                en_day = {}
                energy_list[entry.get('serial')][en_day_str] = en_day
                en_day['date'] = en_day_str
            en_day[entry.get('modbus_id')] = entry.get('max_value') * 10
            
        return energy_list
    
    @classmethod
    def get_energy_daily_output(cls,pvs_serial=None,date_since=None):
        '''return a json data of pvs energy daily output value for specific pvs serial, 
        if pvs_serial is None, it will return all pvs energy daily output json data
        ::
            [
                {'date': 'YYYY-mm-dd', 
                '<modbus_id>': xx, '<modbus_id>': xx, ...},
                ...
            ]
        '''
        DEFAULT_DAY_SINCE = 45
        pvs_serial_list = cls.get_distinct_serial()
        serial_list = []
        if pvs_serial is None:
            serial_list = pvs_serial_list
            logger.debug('param pvs_serial is None, set to all pvs serial')
        else:
            if not pvs_serial in pvs_serial_list:
                logger.warning('error pvs_serial %s param, not exist in db' % pvs_serial)
                return None
            else:
                logger.debug('param pvs_serial = %s' % str(pvs_serial))
                serial_list.append(pvs_serial)
    
        if date_since is None:
            date_since = (datetime.today() + timedelta(days=-DEFAULT_DAY_SINCE)).date()
        logger.debug('param date_since = %s' % str(date_since))

        queryset = Energy.objects.filter(type='en_today',
                                         create_time__date__gte=date_since
                                ).extra({'en_date':'date(create_time)'}
                                ).values('serial','modbus_id','en_date'
                                ).annotate(max_value=Max('value'))
        if not pvs_serial is None:
            queryset = queryset.filter(serial=pvs_serial)
        
        en_daily_list = {}
        for entry in serial_list:
            en_daily_list[entry] = {}
            
        for entry in queryset:
            en_day_str = entry.get('en_date').strftime('%Y-%m-%d')
            en_day = en_daily_list[entry.get('serial')].get(en_day_str,None)
            if en_day is None:
                en_day = {}
                en_daily_list[entry.get('serial')][str(entry.get('en_date'))] = en_day
                en_day['date'] = en_day_str
            en_day[entry.get('modbus_id')] = entry.get('max_value') * 10
            
        return en_daily_list
    
class Weather(models.Model):    
    serial = models.CharField('pi serial', max_length=20)
    create_time = models.DateTimeField('pvs environment weather read time')
    temperature = models.FloatField('temperature value at site',null=True)
    uv = models.IntegerField('UV index at site',null=True)
    visibility = models.FloatField('visibility Index at site',null=True)
    
    
