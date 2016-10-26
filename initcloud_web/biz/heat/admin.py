from django.contrib import admin
from django.contrib import admin

from biz.heat.models import Heat 


#class HeatAdmin(admin.ModelAdmin):
#    list_display = ("user", "mobile", "user_type", "balance")

admin.site.register(Heat)
