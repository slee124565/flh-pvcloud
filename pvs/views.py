from django.shortcuts import render
from django.http import HttpResponse
from django.core import signing
import json
from datetime import datetime

from ipware.ip import get_real_ip

from .models import Report

import logging
logger = logging.getLogger(__name__)

PVS_SECRET_KEY = 'r^ek_^swu&o*_28a%gwn*1x5de8*o^kwhzl^yfv!1qu@6_sz_='

# Create your views here.

def pvs_report_data_update(pvs_info):
    '''parse pvs report data and save into database by model Report
    ::
    
        {
          "ip": "114.34.3.129", 
          "data": {
            "cpuinfo": {
              "hardware": "BCM2709", 
              "serial": "00000000aa80e918", 
              "revision": "a02082"
            }, 
            "version": "v1", 
            "dbconfig": {
              "pvi": [
                {
                  "serial": {
                    "parity": "N", 
                    "baudrate": 9600, 
                    "bytesize": 8, 
                    "timeout": 0.10000000000000001, 
                    "stopbits": 1, 
                    "port": "/dev/ttyUSB0"
                  }, 
                  "type": "DELTA_PRI_H5", 
                  "name": "H5", 
                  "modbus_id": 2
                }
              ], 
              "accuweather": {
                "locationkey": "2516626", 
                "apikey": "ff1b463d98fb47af848ea2843ec5c925", 
                "address": "\u53f0\u5317\u5e02\u627f\u5fb7\u8def\u4e09\u6bb590\u5df7"
              }
            }
          }
        }
    
    '''
    if pvs_info.get('version',None) != 'v1':
        raise Exception('api version error')
    
    pvs_serial = pvs_info.get('data',{}).get('cpuinfo',{}).get('serial',None)
    if pvs_serial is None:
        logging.warning('no pi serial data exist, skip pvs_report process!')
    else: 
        entry, created = Report.objects.get_or_create(serial=pvs_serial)
        if created:
            logging.info('new pvstation report event with serial: %s' % pvs_serial)
        entry.ip = pvs_info.get('ip')
        entry.hardware = pvs_info.get('data',{}).get('cpuinfo',{}).get('hardware','')
        entry.revision = pvs_info.get('data',{}).get('cpuinfo',{}).get('revision','')
        entry.dbconfig = json.dumps(pvs_info.get('data',{}).get('dbconfig',{}))
        entry.last_update_time = datetime.now()
        entry.save()
        logging.info('pvs (%s) report saved' % pvs_serial)
    
def pvs_report(request):

    pvs_ip = get_real_ip(request)
    if pvs_ip == None:
        logger.warning('can not get pvs ip address!')
    else:
        logger.info('pvs report event from ip: %s' % pvs_ip)
    
    
    pvs_encrypt_data = request.POST.get('data',None)
    pvs_data = {}
    if pvs_encrypt_data == None:
        logger.warning('no pvs encrypt data exist!')
    else:
        pvs_data = signing.loads(pvs_encrypt_data,PVS_SECRET_KEY)
        logger.debug('pvs report data with keys: %s' % str(pvs_data.keys()))
    
    pvs_info = {}
    pvs_info['ip'] = pvs_ip
    pvs_info['data'] = pvs_data
    
    pvs_report_data_update(pvs_info)
    
    response = HttpResponse(content_type='text/plain')
    response.content = json.dumps(pvs_info,indent=2)   
    return response
    