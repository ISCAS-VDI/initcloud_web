from django.contrib import admin


from biz.network.models import Network, Subnet, Router


class NetworkAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_default",
                    "user", "user_data_center")


class SubnetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "ip_version",
                    "user", "user_data_center")


class RouterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "gateway",
                    "user", "user_data_center")


admin.site.register(Network, NetworkAdmin)
admin.site.register(Subnet, SubnetAdmin)
admin.site.register(Router, RouterAdmin)
