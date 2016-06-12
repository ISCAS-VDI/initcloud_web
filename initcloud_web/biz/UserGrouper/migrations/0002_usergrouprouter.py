# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('UserGrouper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroupRouter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('param_char1', models.CharField(default=None, max_length=128, verbose_name='Char1')),
                ('param_char2', models.CharField(default=None, max_length=128, verbose_name='Char2')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='UserGrouper.Usergrouper')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
