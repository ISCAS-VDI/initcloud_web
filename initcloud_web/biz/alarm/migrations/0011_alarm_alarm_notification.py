# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0010_alarm_resource_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='alarm_notification',
            field=models.CharField(default=None, max_length=128),
            preserve_default=True,
        ),
    ]
