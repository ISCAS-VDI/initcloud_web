from django.contrib import admin
from biz.volume.models import Volume


class VolumeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "size", "status", "deleted",
                    "user", "user_data_center")


admin.site.register(Volume, VolumeAdmin)


