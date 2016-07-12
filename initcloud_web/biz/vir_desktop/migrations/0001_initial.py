# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VirDesktopAction',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('vm_id', models.CharField(max_length=32)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('state', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
