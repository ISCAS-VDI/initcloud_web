# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0008_auto_20160529_1040'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alarm',
            old_name='ok_actions',
            new_name='alarm_actions',
        ),
    ]
