# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backupitem',
            name='backup',
        ),
        migrations.AddField(
            model_name='backupitem',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='Default Backup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='name',
            field=models.CharField(default='backup', max_length=64, verbose_name='Name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='parent',
            field=models.ForeignKey(related_name='+', to='backup.BackupItem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='progress',
            field=models.IntegerField(default=0, verbose_name='Progress'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='backupitem',
            name='delete_date',
            field=models.DateTimeField(null=True, verbose_name='Delete Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='backupitem',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='backupitem',
            name='rbd_image',
            field=models.CharField(default=None, max_length=256, null=True, verbose_name='RBD Image'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='backupitem',
            name='resource_id',
            field=models.IntegerField(default=-1, verbose_name='Resource ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='backupitem',
            name='resource_type',
            field=models.CharField(default='', max_length=64, verbose_name='Resource'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='backupitem',
            name='resource_uuid',
            field=models.CharField(default='', max_length=64, verbose_name='Backend UUID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='is_full',
            field=models.BooleanField(default=True, verbose_name=b'Full Backup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='chain_id',
            field=models.IntegerField(default=-1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='disk_usage',
            field=models.IntegerField(null=True, default=None),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='backupitem',
            name='resource_name',
        ),
        migrations.RemoveField(
            model_name='backupitem',
            name='resource_size',
        ),
    ]
