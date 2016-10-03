from django.views.generic import TemplateView

class UserPVStationView(TemplateView):
    
    template_name = 'pvstation.html'
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context['pvs_serial'] = self.kwargs.get('pvs_serial')
        return context