# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Heat',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('heatname', models.CharField(max_length=100, verbose_name='Role')),
                ('datacenter', models.IntegerField(default=0, verbose_name='Result')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('description', models.CharField(max_length=255, null=True, verbose_name='Description')),
                ('start_date', models.DateTimeField(default=None, verbose_name='Start Date', auto_now_add=True)),
                ('file_path', models.CharField(max_length=255, null=True, verbose_name='File Paht')),
                ('image_name', models.CharField(default=b'', max_length=255, verbose_name='Image Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
