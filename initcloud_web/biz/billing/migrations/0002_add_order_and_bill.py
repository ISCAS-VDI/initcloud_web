# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('idc', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_id', models.IntegerField()),
                ('resource_type', models.CharField(max_length=20)),
                ('pay_type', models.CharField(max_length=10, choices=[(b'hour', 'Charge By Hour'), (b'month', 'Charge By Month'), (b'year', 'Charge By Year')])),
                ('pay_num', models.IntegerField(default=1)),
                ('cost', models.DecimalField(default=0.0, max_digits=13, decimal_places=4)),
                ('from_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'bill',
                'verbose_name': 'Bill',
                'verbose_name_plural': 'Bill',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BillItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_type', models.CharField(max_length=20, verbose_name='Resource Type', choices=[(b'cpu', 'CPU'), (b'memory', 'Memory'), (b'volume', 'Volume'), (b'floating_ip', 'Floating IP'), (b'bandwidth', 'Band Width'), (b'traffic', 'Traffic')])),
                ('resource_flavor', models.IntegerField(verbose_name='Resource Flavor')),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'bill_item',
                'verbose_name': 'Bill Item',
                'verbose_name_plural': 'Bill Items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BillLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_id', models.IntegerField()),
                ('resource_type', models.CharField(max_length=20)),
                ('old_cost', models.DecimalField(default=0.0, max_digits=13, decimal_places=4)),
                ('new_cost', models.DecimalField(default=0.0, max_digits=13, decimal_places=4)),
                ('price', models.DecimalField(default=0.0, max_digits=13, decimal_places=4)),
                ('old_end_time', models.DateTimeField(default=None, null=True)),
                ('new_end_time', models.DateTimeField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('bill', models.ForeignKey(to='billing.Bill')),
            ],
            options={
                'db_table': 'bill_log',
                'verbose_name': 'Bill Log',
                'verbose_name_plural': 'Bill Logs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_id', models.CharField(max_length=64)),
                ('resource_id', models.IntegerField()),
                ('resource_type', models.CharField(max_length=20, choices=[(b'instance', 'Instance'), (b'floating_ip', 'Floating IP'), (b'volume', 'Volume')])),
                ('pay_type', models.CharField(max_length=10, choices=[(b'hour', 'Charge By Hour'), (b'month', 'Charge By Month'), (b'year', 'Charge By Year')])),
                ('pay_num', models.IntegerField(default=1)),
                ('enabled', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
                ('from_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(default=None, null=True)),
                ('effective_date', models.DateTimeField(auto_now_add=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'resource_order',
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='billlog',
            name='order',
            field=models.ForeignKey(to='billing.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billitem',
            name='order',
            field=models.ForeignKey(related_query_name=b'item', related_name='items', to='billing.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bill',
            name='order',
            field=models.ForeignKey(to='billing.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bill',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bill',
            name='user_data_center',
            field=models.ForeignKey(to='idc.UserDataCenter'),
            preserve_default=True,
        ),
    ]
