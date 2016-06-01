# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PriceRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_type', models.CharField(max_length=20, verbose_name='Resource Type', choices=[(b'cpu', 'CPU'), (b'memory', 'Memory'), (b'volume', 'Volume'), (b'floating_ip', 'Floating IP'), (b'bandwidth', 'Band Width'), (b'traffic', 'Traffic')])),
                ('price_type', models.CharField(default=b'normal', max_length=20, verbose_name='Price Type', choices=[(b'normal', 'Normal'), (b'diff', 'Differential'), (b'linear', 'Linear')])),
                ('hour_price', models.FloatField(default=0.0, verbose_name='Hour Price')),
                ('month_price', models.FloatField(default=0.0, verbose_name='Month Price')),
                ('hour_diff_price', models.FloatField(default=0.0, verbose_name='Hour Differential Price')),
                ('month_diff_price', models.FloatField(default=0.0, verbose_name='Month Differential Price')),
                ('resource_flavor_start', models.IntegerField(default=1, verbose_name='Resource Flavor Start')),
                ('resource_flavor_end', models.IntegerField(default=1, verbose_name='Resource Flavor End')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
                'db_table': 'price_rule',
                'verbose_name': 'Price Rule',
                'verbose_name_plural': 'Price Rules',
            },
            bases=(models.Model,),
        ),
    ]
