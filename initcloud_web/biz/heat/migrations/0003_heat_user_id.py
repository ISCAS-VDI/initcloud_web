# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heat', '0002_auto_20161022_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='heat',
            name='user_id',
            field=models.CharField(max_length=128, null=True, verbose_name=b'user id', blank=True),
            preserve_default=True,
        ),
    ]
