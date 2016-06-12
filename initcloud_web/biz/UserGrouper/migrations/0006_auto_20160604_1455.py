# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserGrouper', '0005_auto_20160604_1450'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usergrouper',
            old_name='UserGroupername',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='usergrouper',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
