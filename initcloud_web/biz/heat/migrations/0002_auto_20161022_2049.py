# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='heat',
            name='deploy_status',
            field=models.BooleanField(default=False, verbose_name='Deploy Status'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='heat',
            name='stack_id',
            field=models.CharField(max_length=128, null=True, verbose_name=b'stack uuid', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='heat',
            name='stack_status_reason',
            field=models.CharField(max_length=255, null=True, verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='heat',
            name='tenant_uuid',
            field=models.CharField(max_length=128, null=True, verbose_name=b'tenant uuid', blank=True),
            preserve_default=True,
        ),
    ]
