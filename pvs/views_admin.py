from django.http import HttpResponse
from django.db.models import Count
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse

from .models import Report, Energy

from datetime import datetime
import json

class PvsManager:
    
    @classmethod
    def prepare_pvs_energy_hourly_output_data(cls, pvs_serial):
        pvs_en_hourly_data = Energy.get_calculated_energy_hourly_output(pvs_serial)[pvs_serial]
        p_date_list = [p_date for p_date in pvs_en_hourly_data]
        p_date_list.sort()
        
        p_data = []
        for p_date in p_date_list:
            p_data.append(pvs_en_hourly_data[p_date])
        
        return p_data

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
            pvs_data[serial] = pvs_report
            
            pvs_report['serial'] = serial
            pvi_data = pvs_report.get('pvi',{})
            pvs_report['pvi'] = pvi_data

            modbus_id = entry.get('modbus_id')
            pvi_report = pvi_data.get(modbus_id,{})
            pvi_data[modbus_id] = pvi_report
            pvi_report['modbus_id'] = modbus_id
            
            pvi_energy = pvi_report.get('energy',{})
            pvi_report['energy'] = pvi_energy
            energy_type = entry.get('type')
            energy = pvi_energy.get(energy_type,{})
            pvi_energy[energy_type] = energy
            energy['non_zero_count'] = entry.get('count')
        return energy_report

class ConsoleMatrixView(TemplateView):
    template_name = 'console_pvs_matrix.html'
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        pvsmatrix = []
        pvslist = []
        row_count = 0 # pagenation usage
        col_count = 0
        for p_serial in Energy.get_distinct_serial():
            p_report = Report.objects.filter(serial=p_serial)[0]
            p_meta = {'serial': p_serial, 
                        'address': json.loads(p_report.dbconfig).get('accuweather').get('address'),
                        'public_ip': p_report.ip,
                        'private_ip': p_report.local_ip,
                        'url': reverse('user_pvs_view',args=(p_serial,)),
                        'last_update_time': p_report.last_update_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'chart_id': 'chart_id_%s' % p_serial,
                        'chart_data_var': 'data_%s' % p_serial,
                        'chart_data_value': json.dumps(PvsManager.prepare_pvs_energy_hourly_output_data(p_serial)),
                        }
            pvslist.append(p_meta)
            col_count += 1
            if col_count % 3 == 0:
                pvsmatrix.append(pvslist)
                pvslist = []
        
        context['pvsmatrix'] = pvsmatrix
        
        return context
    
        
class ConsoleHttpResponse(HttpResponse):
    
    def __init__(self,request):
        super(ConsoleHttpResponse,self).__init__(content_type='text/plain')
        
        serial_list = PvsManager.get_serial_list()
        energy_data = PvsManager.get_today_energy_report()
        
        content = u''
        for entry in serial_list:
            content += u''.join((entry.get('serial'),u' ',entry.get('address'),u'\n',
                            json.dumps(entry.get('data'),indent=4),u'\n\n'))
       
        content += json.dumps(energy_data,indent=4)

        self.content = content
        
def admin_view(request):
    return ConsoleHttpResponse(request)
