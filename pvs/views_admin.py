from django.http import HttpResponse
from .models import *

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
                'pvs' : [
                    {
                        'serial': 'xxxx',
                        'pvi': [
                            {
                                'modbus_id': xxx,
                                'energy': {
                                    'current': {
                                        'count': xxx,
                                        'not_zero': xxx
                                    }
                                }
                            }, ...
                        ]
                    }, ...
                ]
            }
        '''
        energy_report = {}
        #TODO:
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
       
        content += json.dumps(energy_data,indent=4)

        self.content = content
        
def admin_view(request):
    return ConsoleHttpResponse(request)
