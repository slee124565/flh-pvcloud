import os
import json

from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.views.generic import View

from pvs.models import Report, Energy

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
    def get(self, request, pvs_serial=None, *args, **kwargs):
        logger.debug('serial %s' % pvs_serial)
        pvs_meta = {'version':'1.0'}
        
        # TODO: get_pvs_meta
        #-> add pvs address 
        pvs_meta['address'] = Report.get_address(pvs_serial)
        
        return JsonResponse(pvs_meta)
        #logger.debug('resp data: %s' % json.dumps(pvs_meta))
        #return HttpResponse(json.dumps(pvs_meta))