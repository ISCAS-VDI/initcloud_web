# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('volume', '0003_add_detach_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='volume',
            name='os_volume_type',
            field=models.CharField(max_length=128, null=True, verbose_name='OS Volume Type'),
            preserve_default=True,
        ),
    ]
