# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lbaas', '0002_change_session_persistence'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='balancermember',
            options={'verbose_name': 'BalancerMember', 'verbose_name_plural': 'BalancerMember'},
        ),
        migrations.AlterModelOptions(
            name='balancermonitor',
            options={'verbose_name': 'BalancerMonitor', 'verbose_name_plural': 'BalancerMonitor'},
        ),
        migrations.AlterModelOptions(
            name='balancerpool',
            options={'verbose_name': 'BalancerPool', 'verbose_name_plural': 'BalancerPool'},
        ),
        migrations.AlterModelOptions(
            name='balancerpoolmonitor',
            options={'verbose_name': 'BalancerPoolMonitor', 'verbose_name_plural': 'BalancerPoolMonitor'},
        ),
        migrations.AlterModelOptions(
            name='balancervip',
            options={'verbose_name': 'BalancerVIP', 'verbose_name_plural': 'BalancerVIP'},
        ),
        migrations.AlterField(
            model_name='balancervip',
            name='description',
            field=models.CharField(default=b'', max_length=128, verbose_name='Description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='balancervip',
            name='name',
            field=models.CharField(default='vip', max_length=64, verbose_name='Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='balancervip',
            name='protocol_port',
            field=models.IntegerField(default=8000, verbose_name='Protocol port'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='balancervip',
            name='session_persistence',
            field=models.IntegerField(default=-1, verbose_name='Session Persistence', choices=[(-1, 'No Session Persistence'), (0, b'SOURCE_IP'), (1, b'HTTP_COOKIE'), (2, b'APP_COOKIE')]),
            preserve_default=True,
        ),
    ]
