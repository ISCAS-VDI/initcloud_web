from django.contrib import admin

# Register your models here.

from django.contrib import admin
from biz.role.models import Role 


class RoleAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile", "user_type", "balance")

admin.site.register(Role, RoleAdmin)
