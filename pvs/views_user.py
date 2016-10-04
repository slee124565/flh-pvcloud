from django.views.generic import TemplateView

from pvs.models import Energy

import json

class UserPVStationView(TemplateView):
    
    template_name = 'pvstation.html'
    
    ENERGY_DATA_TYPE_TOTAL = 1
    ENERGY_DATA_TYPE_STACKED = 2
    
    def prepare_pvs_energy_hourly_output_data(self, pvs_serial):
        
        pvs_en_hourly_data = Energy.get_calculated_energy_hourly_output(pvs_serial)[pvs_serial]
        p_date_list = [p_date for p_date in pvs_en_hourly_data]
        p_date_list.sort()
        
        p_data = []
        for p_date in p_date_list:
            p_data.append(pvs_en_hourly_data[p_date])
        
        return p_data
        
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
                p_data.append(entry_data)
        elif en_daily_data_type == self.ENERGY_DATA_TYPE_STACKED:
            for p_en_date in p_date_list:
                p_data.append(pvs_en_daily_data[p_en_date])
                
        return p_data
        
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        pvs_serial = self.kwargs.get('pvs_serial')
        if pvs_serial in Energy.get_distinct_serial():
            context['pvs_serial'] = self.kwargs.get('pvs_serial')
            
            pvs_en_daily = self.prepare_pvs_energy_daily_output_data(pvs_serial,self.ENERGY_DATA_TYPE_STACKED)
            context['pvs_data_en_daily'] = json.dumps(pvs_en_daily)
            
            pvs_en_hourly = self.prepare_pvs_energy_hourly_output_data(pvs_serial)
            context['pvs_data_en_hourly'] = json.dumps(pvs_en_hourly)
        return context
    
    