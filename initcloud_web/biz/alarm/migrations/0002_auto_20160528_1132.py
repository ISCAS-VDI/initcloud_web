# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('idc', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('alarm', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alarm',
            name='datacenter',
        ),
        migrations.AddField(
            model_name='alarm',
            name='comparison_operator',
            field=models.CharField(default=b'eq', max_length=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='meter_name',
            field=models.CharField(default=None, max_length=128),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='threshold',
            field=models.IntegerField(default=0.0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='udc',
            field=models.ForeignKey(default=None, to='idc.UserDataCenter'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='user',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='alarm',
            name='alarmname',
            field=models.CharField(max_length=128, verbose_name='Name'),
            preserve_default=True,
        ),
    ]
