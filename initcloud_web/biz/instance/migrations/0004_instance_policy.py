# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0003_auto_20160606_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='policy',
            field=models.IntegerField(default=0, verbose_name='Policy'),
            preserve_default=True,
        ),
    ]
