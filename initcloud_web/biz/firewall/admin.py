#-*- coding=utf-8 -*-

from django.contrib import admin

from biz.firewall.models import Firewall, FirewallRules


class FirewallAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_default", "deleted",
                    "create_date", "user", "user_data_center")

class FirewallRuleAdmin(admin.ModelAdmin):
    list_display = ("id","firewall", "direction", "ether_type", "deleted",
                    "port_range_min", "port_range_max", "protocol",
                    "create_date", "user", "user_data_center")


admin.site.register(Firewall, FirewallAdmin)
admin.site.register(FirewallRules, FirewallRuleAdmin)
