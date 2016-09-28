from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.http.request import HttpRequest
from django.core import signing
from django.core.signing import BadSignature
import json
from datetime import datetime, timedelta

from ipware.ip import get_real_ip

from .models import Report, DbConfig, Energy

import logging
logger = logging.getLogger(__name__)

PVS_SECRET_KEY = 'r^ek_^swu&o*_28a%gwn*1x5de8*o^kwhzl^yfv!1qu@6_sz_='

def pvs_report_data_update_v1(pvs_info):
    '''parse pvs report data and save into database by model Report
    ::
    
        {
          "ip": "114.34.3.129", 
          "local_ip": "192.168.0.100", # v1.1 only
          "data": {
            "cpuinfo": {
              "hardware": "BCM2709", 
              "serial": "00000000aa80e918", 
              "revision": "a02082"
            }, 
            "version": "[v1|v1.1]", 
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
    api_version = pvs_info.get('data',{}).get('version',None)
    if api_version != 'v1':
        logger.warning('error version %s' % pvs_info.get('version',None))
        return
    
    pvs_serial = pvs_info.get('data',{}).get('cpuinfo',{}).get('serial',None)
    if pvs_serial is None:
        logger.warning('no pi serial data exist, skip pvs_report process!')
    else: 
        entry, created = Report.objects.get_or_create(serial=pvs_serial)
        if created:
            logger.info('new pvstation report event with serial: %s' % pvs_serial)
        entry.ip = pvs_info.get('ip')
        if not pvs_info.get('local_ip',None) is None:
            entry.local_ip = pvs_info.get('local_ip')
        entry.hardware = pvs_info.get('data',{}).get('cpuinfo',{}).get('hardware','')
        entry.revision = pvs_info.get('data',{}).get('cpuinfo',{}).get('revision','')
        entry.dbconfig = json.dumps(pvs_info.get('data',{}).get('dbconfig',{}))
        entry.last_update_time = datetime.now()
        entry.save()
        logger.info('pvs (%s) report saved' % pvs_serial)

def pvs_report_data_update(pvs_info):
    api_version = pvs_info.get('data',{}).get('version',None)
    if api_version in ['v1', 'v1.1']:
        pvs_report_data_update_v1(pvs_info)
    else:
        logger.warning('error version %s' % pvs_info.get('version',None))
        return
    
def pvs_report_v1(request):
    '''HTTP POST method for pvs to report it information for pvcloud
    and pvcloud echo the pvs_info for pvs'''

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

class PvsReportHandler_v1(HttpResponse):
    http_request = None
    pvs_serial = None       # pvs pi serial
    pvs_data = None         # decrypted json data from pvstation
    pvs_report = None       # pvs.models.Report class
    
    def __init__(self,http_request):
        super(PvsReportHandler_v1,self).__init__(content_type='text/plain')
        self.http_request = http_request
        
        pvs_encrypt_data = http_request.POST.get('data',None)
        pvs_data = {}
        if pvs_encrypt_data == None:
            logger.warning('no pvs encrypt data exist!')
            return HttpResponseBadRequest('Bad Param Request')
        else:
            pvs_data = signing.loads(pvs_encrypt_data,PVS_SECRET_KEY)
            logger.debug('pvs report data with keys: %s' % str(pvs_data.keys()))
            self.pvs_data = pvs_data
        
        pvs_data['public_ip'] = http_request.POST.get('pvs_public_ip','')
        self.pvs_report = self.get_pvs_report_from_data(pvs_data)
        if self.pvs_report is None:
            return HttpResponseBadRequest('Bad Param Request')
        self.pvs_report.save()
        logger.info('pvs (%s) report saved' % self.pvs_report.serial)

        self.content = json.dumps(pvs_data,indent=2)
            
    def get_pvs_report_from_data(self,pvs_data):
        logger.debug('origin pvs_data: %s' % str(pvs_data))
        pvs_serial = pvs_data.get('cpuinfo',{}).get('serial',None)
        if pvs_serial is None:
            logger.warning('no pi serial data exist, skip pvs_report process!')
            return None
        else: 
            self.pvs_serial = pvs_serial
            entry, created = Report.objects.get_or_create(serial=pvs_serial)
            if created:
                logger.info('new pvstation report event with serial: %s' % pvs_serial)
            entry.ip = pvs_data.get('public_ip')
            if not pvs_data.get('local_ip',None) is None:
                entry.local_ip = pvs_data.get('local_ip')
            entry.hardware = pvs_data.get('cpuinfo',{}).get('hardware','')
            entry.revision = pvs_data.get('cpuinfo',{}).get('revision','')
            entry.dbconfig = json.dumps(pvs_data.get('dbconfig',{}))
            entry.last_update_time = datetime.now()
            return entry

class PvsReportHandler_v1_2(PvsReportHandler_v1):
    pvs_energy_data = None  # pvs energy data list, 
    
    def __init__(self,http_request):
        super(PvsReportHandler_v1_2,self).__init__(http_request)
        self.create_or_update_pvs_energy_data()
        
    def create_or_update_pvs_energy_data(self):
        pvs_energy_data = self.pvs_data.get('energy',None)
        if pvs_energy_data is None:
            logger.warning('no energy data in pvs_data error!')
            return HttpResponseBadRequest('Bad Param Request')
        self.pvs_energy_data = pvs_energy_data
        count_create = 0
        count_update = 0
        for regdata in pvs_energy_data:
            logger.debug('pvs regdata:\n%s' % json.dumps(regdata,indent=2))
            data_id = regdata.get('data_id',None)
            entry,created = Energy.objects.get_or_create(serial = self.pvs_serial,
                                                 data_id = data_id)
            
            if created:
                count_update += 1
                logger.warning('pvs energy data (serial: %s, data_id: %s) already exist, replace it' % (
                                                                    self.pvs_serial, data_id))
            else:
                count_create += 1
            entry.create_time = datetime.strptime(regdata.get('create_time'),'%Y-%m-%d %H:%M:%S')
            logger.debug('entry.create_time: %s' % entry.create_time)
            entry.pvi_name = regdata.get('pvi_name')
            entry.modbus_id = int(regdata.get('modbus_id'))
            entry.value = int(regdata.get('pvi_name'))
            entry.measurement_index = regdata.get('measurement_index')
            entry.save()
            logger.info('pvs energy data (serial: %s, data_id: %s) saved' % (
                                                                    self.pvs_serial, data_id))
        logger.info('pvs energy data %s created and $s updated' % (count_create,count_update))
            
def pvs_report(request,api_version='v1'):
    try:
        request.POST = request.POST.copy()
        request.POST['pvs_public_ip'] = get_real_ip(request)

        if api_version == 'v1':
            return pvs_report_v1(request)
        elif api_version == 'v1_1':
            return PvsReportHandler_v1(request)
        elif api_version == 'v1_2':
            return PvsReportHandler_v1_2(request)
        else:
            logger.warning('Bad Param api_version %s Request' % api_version)
            return HttpResponseBadRequest('Bad Param Request')
    except:
        logger.error('pvs_report web api error', exc_info=True)
        return HttpResponseServerError('Server Internal Error')
    
def pvs_dbconfig(request):
    '''implement web api for pvs self-update dbconfig query feature
    HTTP GET method for pvs to query its new DbConfig
    querystring with sserial=<signed([pi_seria-timestamp])>
    response singing.dumps({'config_id': 'xxx', 'data': <json data>}) 
    data if exist
    
    implement web api for pvs self-update dbconfig acknowledge feature
    HTTP POST method for pvs to ack to server new dbconfig updated
    payload with signing.dumps json data
    { 'config_id' = 'xxx', 'serial': '<pi_serial>', 'result':'pass|fail' }
    '''
    
    if request.method == 'GET':
        sserial = request.GET.get('sserial',None)
        if sserial is None:
            logger.warning('no sserial data exist, skip!')
            return HttpResponseBadRequest('Bad Param Request')
        else:
            serial_time = signing.loads(sserial,PVS_SECRET_KEY)
            if len(serial_time) != 1:
                logger.warning('bad param serial_time %s request' % serial_time)
                return HttpResponseBadRequest('Bad Param Request')
            serial_time = serial_time[0]
            if serial_time.find('-') == -1:
                logger.warning('bad param serial_time %s request' % serial_time)
                return HttpResponseBadRequest('Bad Param Request')
            logger.debug('(serial, signing_time): (%s,%s)' % (serial_time.split('-')[0],serial_time.split('-')[1] ))
            pi_serial = serial_time.split('-')[0]
            signing_time = datetime.strptime(serial_time.split('-')[1],'%Y%m%d%H%M%S')
            logger.debug('(serial,signing_time) : (%s, %s)' % (pi_serial,str(signing_time)))
            if (signing_time+timedelta(minutes=+30) < datetime.now()):
                logger.warning('bad param signing_time %s at time %s' % (str(signing_time),
                                                                         str(datetime.now())))
                return HttpResponseBadRequest('Bad Param Request')
            queryset = DbConfig.objects.filter(serial=pi_serial
                                    ).filter(pvs_updated=False
                                    ).order_by('id')[:1]
            if len(queryset) > 0:
                entry = queryset[0]
                logger.debug('pvs_dbconfig entry:\n %s' % str(entry.__dict__))
                logger.info('new dbconfig for pvs %s with json dump data: %s' % (pi_serial,
                                                                            entry.dbconfig) )
                resp_data = {
                            'config_id': entry.id,
                            'data' : json.loads(entry.dbconfig) 
                            }
            else:
                logger.debug('no dbconfig for pvs %s' % pi_serial)
                resp_data = {}

            response = HttpResponse(content_type='text/plain')
            response.content = signing.dumps(resp_data,PVS_SECRET_KEY)   
            return response
                
    elif request.method == 'POST':
        encrypt_data = request.POST.get('data',None)
        if encrypt_data is None:
            logger.warning('no param data payload')
            return HttpResponseBadRequest('Bad Param Request')
        
        pvs_resp = signing.loads(encrypt_data,PVS_SECRET_KEY)
        config_id = pvs_resp.get('config_id', None)
        if config_id is None:
            logger.warning('no param config_id in pvs response data: %s' % str(pvs_resp))
            return HttpResponseBadRequest('Bad Param Request')
        
        if pvs_resp.get('result','fail') == 'fail':
            logger.info('dbconfig id %s pvs report update fail!' % config_id)
        else:
            dbconfig = DbConfig.objects.get(id=config_id)
            if dbconfig is None:
                logger.warning('pvs report dbconfig id %s not exist!' % config_id)
                return HttpResponseBadRequest('Bad Param Request')
            dbconfig.pvs_update_time = datetime.now()
            dbconfig.pvs_updated = True
            dbconfig.save()
            logger.info('pvs serial (%s) dbconfig id (%s) update success' % (pvs_resp.get('serial'),
                                                                             pvs_resp.get('config_id')))
        
        response = HttpResponse(content_type='text/plain')
        response.content = 'OK'
        return response
    else:
        logger.warning('HTTP method not support, skip' % request.method)
        return HttpResponseBadRequest('Bad Param Request')
