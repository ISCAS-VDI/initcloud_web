# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0001_initial'),
    ]

    def set_disk_size(apps, schema_editor):
        """ set default disk size
        :param apps:
        :param schema_editor:
        :return:
        """

        WINDOWS = 1
        LINUX = 2

        Image = apps.get_model("image", "Image")

        Image.objects.filter(os_type=WINDOWS).update(disk_size=50)
        Image.objects.filter(os_type=LINUX).update(disk_size=30)

    operations = [
        migrations.AddField(
            model_name='image',
            name='disk_size',
            field=models.PositiveIntegerField(default=30, verbose_name='Free Disk'),
            preserve_default=True,
        ),

        migrations.RunPython(set_disk_size),
    ]
