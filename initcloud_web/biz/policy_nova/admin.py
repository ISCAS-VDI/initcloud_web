from django.contrib import admin
from django.contrib import admin

from biz.policy_nova.models import Policy_Nova 


#class Policy_NovaAdmin(admin.ModelAdmin):
#    list_display = ("user", "mobile", "user_type", "balance")

admin.site.register(Policy_Nova)
