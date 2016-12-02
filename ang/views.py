from datetime import date, datetime

import os
import json

from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.views.generic import View

from pvs.models import Report
from pvs.views_user import UserPVStationView

import logging
logger = logging.getLogger(__name__)

class AngularTemplateView(View):
    def get(self, request, item=None, *args, **kwargs):
        print(item)
        template_dir_path = settings.TEMPLATES[0]["DIRS"][0]
        final_path = os.path.join(template_dir_path, item + ".html" )
        try:
            html = open(final_path)
            return HttpResponse(html)
        except:
            raise Http404

class UserAppWebAPIView(View):
    
    @classmethod
    def get_pvs_meat(cls,pvs_serial):
        pvs_meta = {'version':'1.0'}
        dbtool = UserPVStationView()
        
        
        #-> add pvs address 
        pvs_meta['description'] = Report.get_address(pvs_serial)
        pvs_meta['amchart_hourly_data'] = dbtool.prepare_pvs_energy_hourly_output_data(pvs_serial)
        pvs_meta['amchart_daily_data'] = dbtool.prepare_pvs_energy_daily_output_data(pvs_serial,2)
        pvs_meta['amchart_monthly_data'] = dbtool.prepare_pvs_energy_monthly_output_data(pvs_serial)
       
        #-> get energy summary
        pvs_meta['summary'] = {
            'energy': {},
            'carbon': {},
            'profit': {}
            }
        #-> get energy this hour
        last_entry = pvs_meta['amchart_hourly_data'][-1]
        logger.debug('last_entry this hour %s' % last_entry)
        logger.debug('check with %s' % datetime.now().strftime('%Y-%m-%d %H:00:00'))
        MARK_STRING = '-'
        if last_entry['date'] == datetime.now().strftime('%Y-%m-%d %H:00:00'):
            value = 0
            for t_key in last_entry:
                if t_key != 'date':
                    value += last_entry[t_key]
            pvs_meta['summary']['energy']['hour'] = value * 0.001
            pvs_meta['summary']['carbon']['hour'] = value * 0.001 * 0.637
            pvs_meta['summary']['profit']['hour'] = value * 0.001 * 6.8633
        else:
            pvs_meta['summary']['energy']['hour'] = MARK_STRING
            pvs_meta['summary']['carbon']['hour'] = MARK_STRING
            pvs_meta['summary']['profit']['hour'] = MARK_STRING
            
        #-> get energy today
        last_entry = pvs_meta['amchart_daily_data'][-1]
        logger.debug('last_entry today %s' % last_entry)
        logger.debug('check with %s' % date.today().strftime('%Y-%m-%d'))
        if last_entry['date'] == date.today().strftime('%Y-%m-%d'):
            value = 0
            for t_key in last_entry:
                if t_key != 'date':
                    value += last_entry[t_key]
            pvs_meta['summary']['energy']['day'] = value * 0.001
            pvs_meta['summary']['carbon']['day'] = value * 0.001 * 0.637
            pvs_meta['summary']['profit']['day'] = value * 0.001 * 6.8633
        else:
            pvs_meta['summary']['energy']['day'] = MARK_STRING
            pvs_meta['summary']['carbon']['day'] = MARK_STRING
            pvs_meta['summary']['profit']['day'] = MARK_STRING

        #-> get energy this month
        last_entry = pvs_meta['amchart_monthly_data'][-1]
        logger.debug('last_entry this month %s' % last_entry)
        logger.debug('check with %s' % date.today().strftime('%Y-%m'))
        if last_entry['date'] == date.today().strftime('%Y-%m'):
            value = 0
            for t_key in last_entry:
                if t_key != 'date':
                    value += last_entry[t_key]
            pvs_meta['summary']['energy']['month'] = value * 0.001
            pvs_meta['summary']['carbon']['month'] = value * 0.001 * 0.637
            pvs_meta['summary']['profit']['month'] = value * 0.001 * 6.8633
        else:
            pvs_meta['summary']['energy']['month'] = MARK_STRING
            pvs_meta['summary']['carbon']['month'] = MARK_STRING
            pvs_meta['summary']['profit']['month'] = MARK_STRING
        
        return pvs_meta
        
    def get(self, request, pvs_serial=None, *args, **kwargs):
        logger.debug('serial %s' % pvs_serial)
        return JsonResponse(UserAppWebAPIView.get_pvs_meat(pvs_serial))
        #logger.debug('resp data: %s' % json.dumps(pvs_meta))
        #return HttpResponse(json.dumps(pvs_meta))