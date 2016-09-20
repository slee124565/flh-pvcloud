from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def pvs_report(request):
    response = HttpResponse(content_type='text/plain')
    from ipware.ip import get_real_ip
    pvs_ip = get_real_ip(request)
    if pvs_ip is not None:
       response.content = 'pvs_ip address is %s.' % pvs_ip
    else:
       response.content = 'pvs_ip address is %s.' % pvs_ip
       
    return response
    