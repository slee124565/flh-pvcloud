from __future__ import unicode_literals

from django.db import models
from django.db.models import Count, Max
from datetime import datetime, date, timedelta

import json
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
    
    @classmethod
    def get_address(cls, pvs_serial):
        queryset = cls.objects.filter(serial=pvs_serial).order_by('-last_update_time')
        if len(queryset) > 0:
            entry = queryset[0]
            dbconfig = json.loads(entry.dbconfig)
            return dbconfig.get('accuweather').get('address')
        else:
            return pvs_serial

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
        DEFAULT_DAY_SINCE = 2
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
        DEFAULT_DAY_SINCE = 30
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
                                         create_time__date__gte=date_since,
                                         create_time__hour__gte=3
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
    
    @classmethod
    def get_monthly_output(cls,pvs_serial=None,date_since=None):
        '''return a json data of pvs energy monthly output value for specific pvs serial, 
        if pvs_serial is None, it will return all pvs energy daily output json data
        ::
            [
                {'date': 'YYYY-mm', 
                '<modbus_id>': xx, '<modbus_id>': xx, ...},
                ...
            ]
        '''
        DEFAULT_MONTH_SINCE = 12
        if date_since is None:
            date_since = (datetime.today() + timedelta(days=-DEFAULT_MONTH_SINCE*30)).date()
            date_since = date(date_since.year,date_since.month,1)
        logger.debug('param date_since = %s' % str(date_since))
        
        eng_daily_output = cls.get_energy_daily_output(pvs_serial, date_since)
        logger.debug('get energy daily output count %d since %s' % (len(eng_daily_output), date_since))

        eng_montly_list = {}
        for t_serial in eng_daily_output:
            logger.debug('processing pvs serial %s' % t_serial)
            t_pvs_eng_monthly_list = {}
            t_pvs_daily_list = eng_daily_output[t_serial]
            eng_montly_list[t_serial] = t_pvs_eng_monthly_list
            logger.debug('pvs %s with entry count %d' % (t_serial,len(t_pvs_daily_list)))
            
            t_pvs_date_list = sorted(t_pvs_daily_list.keys())
            #-> skip first month data if not start from the first day of that month
            while (len(t_pvs_date_list) > 0):
                t_date = t_pvs_date_list[0]
                if t_date[len('YYYY-mm-'):len('YYYY-mm-')+2] != '01':
                    logger.debug('skip date %s with day %s' % (t_pvs_date_list[0],
                                                               t_date[len('YYYY-mm-')+1:len('YYYY-mm-')+3]))
                    del t_pvs_date_list[0]
                else:
                    logger.debug('pvs montly eng since date %s' % t_pvs_date_list[0])   
                    break
                
            for t_date in t_pvs_date_list:
                t_day_entry = t_pvs_daily_list[t_date]
                t_month_key = t_date[:len('YYYY-mm')]
                if not t_month_key in t_pvs_eng_monthly_list:
                    eng_month = {'date': t_month_key}
                    for t_key in t_day_entry:
                        if t_key != 'date':
                            eng_month[t_key] = t_day_entry[t_key]
                    t_pvs_eng_monthly_list[t_month_key] = eng_month
                    logger.debug('eng_month initial: %s' % eng_month)
                else:
                    eng_month = t_pvs_eng_monthly_list[t_month_key]
                    for t_key in t_day_entry:
                        if t_key != 'date':
                            if t_key in eng_month:
                                eng_month[t_key] += t_day_entry[t_key]
                            else:
                                eng_month[t_key] = t_day_entry[t_key]
                    logger.debug('eng_month update: %s' % eng_month)
        logger.debug('final %s' % eng_montly_list)
        return eng_montly_list
    
    @classmethod
    def get_yearly_output(cls,pvs_serial=None,date_since=None):
        '''return a json data of pvs energy monthly output value for specific pvs serial, 
        if pvs_serial is None, it will return all pvs energy daily output json data
        ::
            [
                {'date': 'YYYY', 
                '<modbus_id>': xx, '<modbus_id>': xx, ...},
                ...
            ]
        '''
        DEFAULT_YEAR_SINCE = 4
        if date_since is None:
            date_since = (datetime.today() + timedelta(days=-DEFAULT_YEAR_SINCE*365)).date()
            date_since = date(date_since.year,date_since.month,1)
        logger.debug('param date_since = %s' % str(date_since))
        
        eng_daily_output = cls.get_energy_daily_output(pvs_serial, date_since)
        logger.debug('get energy daily output count %d since %s' % (len(eng_daily_output), date_since))

        eng_yearly_list = {}
        for t_serial in eng_daily_output:
            logger.debug('processing pvs serial %s' % t_serial)
            t_pvs_eng_yearly_list = {}
            t_pvs_daily_list = eng_daily_output[t_serial]
            eng_yearly_list[t_serial] = t_pvs_eng_yearly_list
            logger.debug('pvs %s with entry count %d' % (t_serial,len(t_pvs_daily_list)))
            
            t_pvs_date_list = sorted(t_pvs_daily_list.keys())
                
            for t_date in t_pvs_date_list:
                t_day_entry = t_pvs_daily_list[t_date]
                t_year_key = t_date[:len('YYYY')]
                if not t_year_key in t_pvs_eng_yearly_list:
                    eng_year = {'date': t_year_key}
                    for t_key in t_day_entry:
                        if t_key != 'date':
                            eng_year[t_key] = t_day_entry[t_key]
                    t_pvs_eng_yearly_list[t_year_key] = eng_year
                    logger.debug('eng_year initial: %s' % eng_year)
                else:
                    eng_year = t_pvs_eng_yearly_list[t_year_key]
                    for t_key in t_day_entry:
                        if t_key != 'date':
                            if t_key in eng_year:
                                eng_year[t_key] += t_day_entry[t_key]
                            else:
                                eng_year[t_key] = t_day_entry[t_key]
                    logger.debug('eng_year update: %s' % eng_year)
        logger.debug('final %s' % eng_yearly_list)
        return eng_yearly_list

class Weather(models.Model):    
    serial = models.CharField('pi serial', max_length=20)
    create_time = models.DateTimeField('pvs environment weather read time')
    temperature = models.FloatField('temperature value at site',null=True)
    uv = models.IntegerField('UV index at site',null=True)
    visibility = models.FloatField('visibility Index at site',null=True)
    
class EnergyData(models.Model):
    '''sync with pvstation db table pvs_energydata'''
    serial = models.CharField('pi serial', max_length=20)
    data_id = models.IntegerField('rowdata id in pvs',null=True)
    modbus_id = models.IntegerField('modbus address',null=True)
    datetime = models.DateTimeField('energy date',null=True)
    type = models.CharField('energy type',max_length=20,null=True)
    value = models.IntegerField('energy value',null=True)
    
    def __str__(self):
        return str(('EnergyData', self.serial,self.data_id,self.modbus_id,
                                    self.datetime,self.type,self.value))    
    
