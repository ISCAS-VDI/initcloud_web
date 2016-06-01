# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0007_auto_20160528_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='has_resource',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='resource_id',
            field=models.CharField(default=None, max_length=128),
            preserve_default=True,
        ),
    ]
