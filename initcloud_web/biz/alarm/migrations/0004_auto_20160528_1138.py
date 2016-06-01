# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0003_auto_20160528_1134'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alarm',
            old_name='udc',
            new_name='user_data_center',
        ),
    ]
