from django.contrib import admin
from .models import DbConfig, Report

# Register your models here.
admin.site.register(DbConfig)
admin.site.register(Report)