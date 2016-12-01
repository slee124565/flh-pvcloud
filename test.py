#!/usr/bin/env python
import os
import sys
import django
import json
from datetime import timedelta, datetime, date

pvs_serial = '0000000097894c9b'
#pvs_serial = '00000000f6392e07' # tainan

def test_pvs_energy_montly():
    from pvs.models import Energy
    
    pvs_serial = None
    pvs_en_list = Energy.get_monthly_output(pvs_serial)
    print('origin data: %s' % pvs_en_list)
    
    for pvs_serial in pvs_en_list:
        result_list = []
        for entry in pvs_en_list[pvs_serial].values():
            result_list.append(entry.values())
        result_list.sort(key=lambda x: x[0])
        print('== pvs %s energy monthly result ==' % pvs_serial)
        for entry in result_list:
            print(entry)

def test_pvs_energy_daily():
    from pvs.models import Energy

    DEFAULT_MONTH_SINCE = 18
    date_since = (datetime.today() + timedelta(days=-DEFAULT_MONTH_SINCE*30)).date()
    date_since = date(date_since.year,date_since.month,1)
    print('date since %s' % date_since)

    pvs_en_daily = Energy.get_energy_daily_output(pvs_serial, date_since)
    
    result_list = []
    for entry in pvs_en_daily[pvs_serial].values():
        result_list.append(entry.values())
    result_list.sort(key=lambda x: x[0])
    print('== pvs energy today daily result ==')
    for entry in result_list:
        print(entry)

    
def test_pvs_energy_hourly():
    from pvs.models import Energy
    
    pvs_list = Energy.get_distinct_serial()
    print('distinct pvs serial: %s' % pvs_list)
    
    #pvs_serial = '0000000097894c9b'
    pvs_serial = '00000000f6392e07'
    pvs_en_by_hour = Energy.get_energy_daily_output_by_hour(pvs_serial)
    #print(pvs_en_by_hour)
    #return
    result_list = []
    for entry in pvs_en_by_hour[pvs_serial].values():
        result_list.append(entry.values())
    result_list.sort(key=lambda x: x[0])
    print('== pvs energy today hourly result ==')
    for entry in result_list:
        print(entry)
        
    pvs_en_hourly = Energy.get_calculated_energy_hourly_output(pvs_serial)
    result_list = []
    for entry in pvs_en_hourly[pvs_serial].values():
        result_list.append(entry.values())
    result_list.sort(key=lambda x: x[0])
    print('== pvs calculated energy hourly result ==')
    for entry in result_list:
        print(entry)
    
    
    
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    django.setup()
    
    #test_pvs_energy_hourly()
    #test_pvs_energy_daily()
    test_pvs_energy_montly()
