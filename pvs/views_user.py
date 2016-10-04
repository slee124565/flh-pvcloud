from django.views.generic import TemplateView

from pvs.models import Energy

import json

class UserPVStationView(TemplateView):
    
    template_name = 'pvstation.html'
    
    def prepare_pvs_energy_daily_output_data(self,pvs_serial):
        
        pvs_en_daily_data = Energy.get_energy_daily_output(pvs_serial)[pvs_serial]
        p_date_list = [entry for entry in pvs_en_daily_data]
        p_date_list.sort()
        
        p_data = []
        for p_en_date in p_date_list:
            entry_data = { 'date': p_en_date,
                          'energy': 0}
            for key in pvs_en_daily_data[p_en_date]:
                if key != 'date':
                    entry_data['energy'] += pvs_en_daily_data[p_en_date][key]
            p_data.append(entry_data)
        return p_data
        
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        pvs_serial = self.kwargs.get('pvs_serial')
        if pvs_serial in Energy.get_distinct_serial():
            context['pvs_serial'] = self.kwargs.get('pvs_serial')
            pvs_en_daily = self.prepare_pvs_energy_daily_output_data(pvs_serial)
            context['pvs_data_en_daily'] = json.dumps(pvs_en_daily)
        return context