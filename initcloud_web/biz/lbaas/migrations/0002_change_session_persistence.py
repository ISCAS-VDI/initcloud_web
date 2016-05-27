# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lbaas', '0001_initial'),
    ]

    def convert_session_persistence_of_vip(apps, schema_editor):
        """ Convert session persistence of vip to -1 when its value is None
        :param apps:
        :param schema_editor:
        :return:
        """

        BalancerVIP = apps.get_model("lbaas", "BalancerVIP")

        for vip in BalancerVIP.objects.all():
            if vip.session_persistence is None:
                vip.session_persistence = -1
                vip.save()

    operations = [
        migrations.RunPython(convert_session_persistence_of_vip),

    ]
