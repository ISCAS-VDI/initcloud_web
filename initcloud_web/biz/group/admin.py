from django.contrib import admin
from django.contrib import admin

from biz.group.models import Group 


#class GroupAdmin(admin.ModelAdmin):
#    list_display = ("user", "mobile", "user_type", "balance")

admin.site.register(Group)
