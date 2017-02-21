from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from pvs.models import Energy, Report

from datetime import date
import json
import logging
from django.views.generic.base import View

logger = logging.getLogger(__name__)

class UserPVStationView2(View):

    def get(self, request, pvs_serial, *args, **kwargs):
        print(pvs_serial)
        return redirect(reverse('user_pvs_view') + '#/userSite/' + pvs_serial)

#-> deprecated by UserPVStationView2
class UserPVStationView(TemplateView):
    
    template_name = 'pvstation.html'
    
    ENERGY_DATA_TYPE_TOTAL = 1
    ENERGY_DATA_TYPE_STACKED = 2
    
    @classmethod
    def turn_energy_into_kwh_unit(cls, p_data):
        for entry in p_data:
            for key in entry:
                if key != 'date':
                    entry[key] = round((entry[key] * 0.001),2)
        return p_data
    
    def prepare_pvs_energy_hourly_output_data(self, pvs_serial):
        
        pvs_en_hourly_data = Energy.get_calculated_energy_hourly_output(pvs_serial)[pvs_serial]
        p_date_list = [p_date for p_date in pvs_en_hourly_data]
        p_date_list.sort()
        
        p_data = []
        for p_date in p_date_list:
            p_data.append(pvs_en_hourly_data[p_date])
        
        return UserPVStationView.turn_energy_into_kwh_unit(p_data)
        
    def prepare_pvs_energy_daily_output_data(self,pvs_serial,en_daily_data_type=ENERGY_DATA_TYPE_TOTAL):
        
        pvs_en_daily_data = Energy.get_energy_daily_output(pvs_serial)[pvs_serial]
        p_date_list = [entry for entry in pvs_en_daily_data]
        p_date_list.sort()
        
        p_data = []
        if en_daily_data_type == self.ENERGY_DATA_TYPE_TOTAL:
            for p_en_date in p_date_list:
                entry_data = { 'date': p_en_date,
                              'energy': 0}
                for key in pvs_en_daily_data[p_en_date]:
                    if key != 'date':
                        entry_data['energy'] += pvs_en_daily_data[p_en_date][key]
                p_data.append([entry_data[0],entry_data[1]*0.001])
        elif en_daily_data_type == self.ENERGY_DATA_TYPE_STACKED:
            for p_en_date in p_date_list:
                p_data.append(pvs_en_daily_data[p_en_date])
                
        return UserPVStationView.turn_energy_into_kwh_unit(p_data)
    
    def prepare_pvs_energy_monthly_output_data(self,pvs_serial):
        pvs_en_monthly_data = Energy.get_monthly_output(pvs_serial)[pvs_serial]
        logger.debug('pvs_en_monthly_data count %d' % len(pvs_en_monthly_data))
        p_date_list = pvs_en_monthly_data.keys()
        p_date_list = sorted(p_date_list)
        logger.debug('p_date_list count %d' % len(p_date_list))
        
        p_data = []
        for p_en_date in p_date_list:
            p_data.append(pvs_en_monthly_data[p_en_date])
        
        return UserPVStationView.turn_energy_into_kwh_unit(p_data)

    def prepare_pvs_energy_yearly_output_data(self,pvs_serial):
        pvs_en_yearly_data = Energy.get_yearly_output(pvs_serial)[pvs_serial]
        logger.debug('pvs_en_yearly_data count %d' % len(pvs_en_yearly_data))
        p_date_list = pvs_en_yearly_data.keys()
        p_date_list = sorted(p_date_list)
        logger.debug('p_date_list count %d' % len(p_date_list))
        
        p_data = []
        for p_en_date in p_date_list:
            p_data.append(pvs_en_yearly_data[p_en_date])
        
        return UserPVStationView.turn_energy_into_kwh_unit(p_data)
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        pvs_serial = self.kwargs.get('pvs_serial')
        if pvs_serial in Energy.get_distinct_serial():
            context['pvs_serial'] = self.kwargs.get('pvs_serial')
            
            pvs_en_daily = self.prepare_pvs_energy_daily_output_data(pvs_serial,self.ENERGY_DATA_TYPE_STACKED)
            context['pvs_data_en_daily'] = json.dumps(pvs_en_daily)
            
            pvs_en_hourly = self.prepare_pvs_energy_hourly_output_data(pvs_serial)
            context['pvs_data_en_hourly'] = json.dumps(pvs_en_hourly)
            
            context['pvs_address'] = u''.join(Report.get_address(pvs_serial)).encode('utf-8')
            
            context['copyright_year'] = date.today().year
            
        return context

    
    