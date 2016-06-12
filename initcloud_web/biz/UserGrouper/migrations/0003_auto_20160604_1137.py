# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserGrouper', '0002_usergrouprouter'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergrouprouter',
            name='deleted',
            field=models.BooleanField(default=False, verbose_name='Deleted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usergrouprouter',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
