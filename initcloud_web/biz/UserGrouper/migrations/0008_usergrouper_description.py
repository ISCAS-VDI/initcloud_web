# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserGrouper', '0007_auto_20160604_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergrouper',
            name='description',
            field=models.CharField(default=b'', max_length=128, verbose_name='Description'),
            preserve_default=True,
        ),
    ]
