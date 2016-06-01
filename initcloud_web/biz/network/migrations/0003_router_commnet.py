# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_add_user_udc_to_routerinterface'),
    ]

    operations = [
        migrations.AlterField(
            model_name='router',
            name='gateway',
            field=models.CharField(max_length=128, null=True, verbose_name='Gateway IP Address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='router',
            name='is_gateway',
            field=models.BooleanField(default=False, verbose_name='Has Gateway Setted'),
            preserve_default=True,
        ),
    ]
