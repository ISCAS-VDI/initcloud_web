# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserGrouper', '0006_auto_20160604_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergrouprouter',
            name='deleted',
            field=models.BooleanField(default=True, verbose_name='Deleted'),
            preserve_default=True,
        ),
    ]
