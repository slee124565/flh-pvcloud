from django.http import HttpResponse
from django.db.models import Count

from .models import Report, Energy

from datetime import datetime
import json

class PvsManager:
    
    @classmethod
    def get_serial_list(cls):
        '''return a list of distinct pvs serial from pvs_report table
        ex: 
            [('serial','address'), ...]
        '''
        serial_list = [{'address': json.loads(entry.dbconfig).get('accuweather').get('address'),
                        'serial': entry.serial,
                        'data': {
                            'local ip': entry.local_ip,
                            'public ip': entry.ip}} for entry in Report.objects.all()]
        return serial_list
    
    @classmethod
    def get_today_energy_report(cls):
        '''return today energy report json data
        ex:
            {
                'date' : 'YYYY-mm-dd',
                'pvs' : {
                    '<serial>':
                        {
                            'serial': 'xxxx',
                            'pvi': {
                                <modbus_id>:
                                    {
                                        'modbus_id': xxx,
                                        'energy': {
                                            'current': {
                                                'count': xxx,
                                                'not_zero': xxx
                                            }
                                        }
                                    }
                            }, ...
                        }
                }, ...
            }
        '''
        energy_report = {
            'date': datetime.today().date().strftime('%Y-%m-%d'),
            'pvs': {}
            }

        queryset = Energy.objects.filter(create_time__gt=datetime.today().date()
                                ).filter(value__gt=0
                                ).values('serial','modbus_id','type'
                                ).annotate(count=Count(type))
        for entry in queryset:
            pvs_data = energy_report.get('pvs',{})
            energy_report['pvs'] = pvs_data
            
            serial = entry.get('serial')
            pvs_report = pvs_data.get(serial,{})
            pvs_report[serial]['serial'] = entry.get('serial')

            modbus_id = entry.get('modbus_id')
            pvi_report = pvs_report.get(modbus_id,{})
            pvi_report[modbus_id]['modbus_id'] = modbus_id
            
            pvi_energy = pvi_report[modbus_id].get('energy',{})
            energy_type = entry.get('type')
            pvi_energy = pvi_energy.get(energy_type,{})
            pvi_energy[energy_type]['non_zero_count'] = entry.get('count')
        return energy_report
    
class ConsoleHttpResponse(HttpResponse):
    
    def __init__(self,request):
        super(ConsoleHttpResponse,self).__init__()
        self.content_type = 'plain/text'
        
        serial_list = PvsManager.get_serial_list()
        energy_data = PvsManager.get_today_energy_report()
        
        content = u''
        for entry in serial_list:
            content += u''.join((entry.get('serial'),u' ',entry.get('address'),u'<br/>',
                            json.dumps(entry.get('data'),indent=4),u'<br/><br/>'))
       
        content += json.dumps(energy_data,indent=4).replace(u'\n',u'<br/>')

        self.content = content
        
def admin_view(request):
    return ConsoleHttpResponse(request)
