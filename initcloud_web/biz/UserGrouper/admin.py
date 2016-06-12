from django.contrib import admin
from django.contrib import admin

from biz.UserGrouper.models import Usergrouper, UserGroupRouter 


#class UsergrouperAdmin(admin.ModelAdmin):
#    list_display = ("user", "mobile", "user_type", "balance")

admin.site.register(Usergrouper)
admin.site.register(UserGroupRouter)
