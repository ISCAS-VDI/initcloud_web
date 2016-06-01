# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0005_auto_20160528_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='alarm_ins_id',
            field=models.CharField(default=None, max_length=128),
            preserve_default=True,
        ),
    ]
