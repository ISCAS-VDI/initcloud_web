#coding=utf-8

from django.contrib import admin

from biz.instance.models import Instance, Flavor


class InstanceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "private_ip", "public_ip", "deleted",
                    "create_date", "user", "user_data_center")


class FlavorAdmin(admin.ModelAdmin):
    list_display = ("name", "cpu", "memory")



admin.site.register(Instance, InstanceAdmin)
admin.site.register(Flavor, FlavorAdmin)
