# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0002_add_audit_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='flavor',
            name='disk',
            field=models.IntegerField(default=10, verbose_name='Disk'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flavor',
            name='flavorid',
            field=models.CharField(default=None, max_length=128, verbose_name='FlavorId'),
            preserve_default=True,
        ),
    ]
