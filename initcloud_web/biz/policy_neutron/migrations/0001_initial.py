# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Policy_Neutron',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('action', models.CharField(default=None, max_length=128, verbose_name='Action')),
                ('role', models.CharField(default=None, max_length=128, verbose_name='Role')),
                ('datacenter', models.IntegerField(default=0, verbose_name='Result')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
            ],
            options={
                'db_table': 'policy_neutron',
            },
            bases=(models.Model,),
        ),
    ]
