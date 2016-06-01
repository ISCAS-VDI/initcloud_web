# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lbaas', '0004_refactor_monitor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balancerpool',
            name='lb_method',
            field=models.IntegerField(verbose_name='Lb method', choices=[(0, 'Round Robin'), (1, 'Least Connection'), (2, 'Source IP')]),
            preserve_default=True,
        ),
    ]
