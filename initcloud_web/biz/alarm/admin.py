from django.contrib import admin
from django.contrib import admin

from biz.alarm.models import Alarm 


#class AlarmAdmin(admin.ModelAdmin):
#    list_display = ("user", "mobile", "user_type", "balance")

admin.site.register(Alarm)
