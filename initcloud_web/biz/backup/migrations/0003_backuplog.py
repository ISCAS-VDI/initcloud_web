# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0002_refactor_backup_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackupLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=10)),
                ('duration', models.IntegerField(default=0)),
                ('is_success', models.BooleanField(default=False)),
                ('progress', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=64, null=True, verbose_name='Name')),
                ('rbd_image', models.CharField(default=None, max_length=256, null=True)),
                ('disk_usage', models.IntegerField(default=None, null=True)),
                ('resource_id', models.IntegerField()),
                ('resource_uuid', models.CharField(max_length=64)),
                ('resource_type', models.CharField(max_length=64)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('item', models.ForeignKey(related_query_name=b'log', related_name='logs', to='backup.BackupItem', null=True)),
            ],
            options={
                'db_table': 'backup_log',
                'verbose_name': 'Backup Log',
                'verbose_name_plural': 'Backup Log',
            },
            bases=(models.Model,),
        ),
    ]
