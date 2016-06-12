# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserGrouper', '0003_auto_20160604_1137'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usergrouprouter',
            old_name='user_data_center',
            new_name='group',
        ),
        migrations.RemoveField(
            model_name='usergrouper',
            name='datacenter',
        ),
    ]
