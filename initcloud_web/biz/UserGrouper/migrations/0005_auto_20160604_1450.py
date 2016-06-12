# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserGrouper', '0004_auto_20160604_1441'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usergrouprouter',
            name='param_char1',
        ),
        migrations.RemoveField(
            model_name='usergrouprouter',
            name='param_char2',
        ),
        migrations.AddField(
            model_name='usergrouper',
            name='param_char1',
            field=models.CharField(default=None, max_length=128, verbose_name='Char1'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usergrouper',
            name='param_char2',
            field=models.CharField(default=None, max_length=128, verbose_name='Char2'),
            preserve_default=True,
        ),
    ]
