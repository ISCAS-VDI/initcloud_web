# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0004_instance_policy'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='tenant_uuid',
            field=models.CharField(max_length=128, null=True, verbose_name=b'tenant uuid', blank=True),
            preserve_default=True,
        ),
    ]
