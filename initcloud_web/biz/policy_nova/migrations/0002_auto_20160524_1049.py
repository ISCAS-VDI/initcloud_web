# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('policy_nova', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policy_nova',
            name='policy_novaname',
        ),
        migrations.AddField(
            model_name='policy_nova',
            name='action',
            field=models.CharField(default=None, max_length=128, verbose_name='Action'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='policy_nova',
            name='role',
            field=models.CharField(default=None, max_length=128, verbose_name='Role'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='policy_nova',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
