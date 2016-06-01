from django.contrib import admin
from django.contrib import admin

from biz.policy_neutron.models import Policy_Neutron


#class Policy_NovaAdmin(admin.ModelAdmin):
#    list_display = ("user", "mobile", "user_type", "balance")

admin.site.register(Policy_Neutron)
