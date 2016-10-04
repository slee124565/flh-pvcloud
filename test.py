#!/usr/bin/env python
import os
import sys
import django
import json


def test_pvs_energy_daily():
    from pvs.models import Energy

    pvs_serial = '0000000097894c9b'
    pvs_en_daily = Energy.get_energy_daily_output(pvs_serial)
    
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
    
    pvs_serial = '0000000097894c9b'
    #pvs_serial = '00000000f6392e07'
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
    test_pvs_energy_daily()
