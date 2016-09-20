from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Report(models.Model):
    ip = models.CharField('pvs ip address', max_length=20)
    hardware = models.CharField('pi hardware', max_length=20)
    revision = models.CharField('pi revision', max_length=20)
    serial = models.CharField('pi serial', max_length=20)
    dbconfig = models.TextField('pvs dbconfig', default='{}')
    last_update_time = models.DateTimeField('last update time')