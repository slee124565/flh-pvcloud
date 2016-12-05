"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from mysite import sphinx_doc_view

from pvs.views import pvs_report, pvs_dbconfig

from pvs.views_admin import admin_view
#from console.views import webapp_console

from pvs.views_user import UserPVStationView, UserPVStationView2
from pvs.views_admin import ConsoleMatrixView

from ang.views import AngularTemplateView, UserAppWebAPIView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # -- backend api -- #
    url(r'^pvs/report/$', csrf_exempt(pvs_report)),
    url(r'^pvs/report/(?P<api_version>\w+)/$', csrf_exempt(pvs_report)),
    url(r'^pvs/dbconfig/$', csrf_exempt(pvs_dbconfig)),
    
    url(r'^console/all/$', admin_view),
    #url(r'^console/$', webapp_console),
    url(r'^console/$', ConsoleMatrixView.as_view(),name='console_matrix_view'),

    #url(r'^user/site/(?P<pvs_serial>\w+)/$', UserPVStationView.as_view(),name='user_pvs_view_v1'),
    url(r'^user/site/(?P<pvs_serial>\w+)/$', UserPVStationView2.as_view(),name='user_pvs_view_v1'),

    # -- angJS app view -- #
    url(r'^uapp/$', 
        TemplateView.as_view(template_name='ang/user_webapp.html'), name='user_pvs_view'),    
    url(r'^uapp/views/(?P<item>[A-Za-z0-9\_\-\.\/]+)\.html$',  AngularTemplateView.as_view()),
    url(r'^uapp/api/(?P<pvs_serial>\w+)$', UserAppWebAPIView.as_view()),

    # -- default page -- #
    url(r'^$', sphinx_doc_view),
    
]
