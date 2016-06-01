# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0006_alarm_alarm_ins_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='ok_actions',
            field=models.CharField(default=None, max_length=128),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='severity',
            field=models.CharField(default=b'low', max_length=128),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='statistic',
            field=models.CharField(default=b'avg', max_length=128),
            preserve_default=True,
        ),
    ]
