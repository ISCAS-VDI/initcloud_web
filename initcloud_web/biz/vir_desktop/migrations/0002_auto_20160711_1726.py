# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vir_desktop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virdesktopaction',
            name='vm_id',
            field=models.CharField(max_length=128),
            preserve_default=True,
        ),
    ]
