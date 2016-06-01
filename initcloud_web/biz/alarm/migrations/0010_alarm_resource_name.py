# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0009_auto_20160529_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='resource_name',
            field=models.CharField(default=None, max_length=128),
            preserve_default=True,
        ),
    ]
