# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0002_auto_20160528_1132'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='alarm',
            table='alarm',
        ),
    ]
