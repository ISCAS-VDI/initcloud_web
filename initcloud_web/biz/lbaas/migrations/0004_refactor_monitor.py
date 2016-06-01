# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lbaas', '0003_refactor_balancer_vip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balancermonitor',
            name='delay',
            field=models.IntegerField(null=True, verbose_name='Delay'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='balancermonitor',
            name='http_method',
            field=models.CharField(default=b'GET', max_length=10, null=True, verbose_name='Http method', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='balancermonitor',
            name='timeout',
            field=models.IntegerField(null=True, verbose_name='Timeout'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='balancermonitor',
            name='url_path',
            field=models.CharField(default=b'/', max_length=80, null=True, verbose_name='Url path', blank=True),
            preserve_default=True,
        ),
    ]
