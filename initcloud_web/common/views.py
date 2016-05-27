#!/usr/bin/env python
# coding=utf-8

import json
import logging

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from biz.instance import settings as instance_settings
from biz.floating import settings as floating_settings
from biz.network import settings as network_settings
from biz.volume import settings as volume_settings
from biz.lbaas import settings as lbaas_settings
from biz.backup import settings as backup_settings
from biz.account.models import UserProxy
from biz.idc.models import DataCenter
from cloud.api import neutron
from cloud.cloud_utils import create_rc_by_dc

from devops.machine.settings import PXE_STATUS
from devops.patrol.settings import (PATROL_ITEM_CATEGORY,
                                    PATROL_TASK_REPEAT_CHOICE)
from devops.maint.settings import (MAINT_ITEM_CATEGORY, MAINT_TASK_CATEGORY,
                                   MAINT_RESULT_STATUS)

LOG = logging.getLogger(__name__)


def state_service(request):

    params = (
        (instance_settings,
         instance_settings.INSTANCE_STATES,
         instance_settings.INSTANCE_STATES_DICT,
         'INSTANCE_STATE_', 'InstanceState'),

        (floating_settings,
         floating_settings.FLOATING_STATUS,
         floating_settings.FLOATING_STATUS_DICT,
         'FLOATING_', 'FloatingState'),

        (network_settings,
         network_settings.NETWORK_STATES,
         network_settings.NETWORK_STATES_DICT,
         'NETWORK_STATE_', 'NetworkState'),

        (volume_settings,
         volume_settings.VOLUME_STATES,
         volume_settings.VOLUME_STATES_DICT,
         'VOLUME_STATE_', 'VolumeState'),

        (lbaas_settings,
         lbaas_settings.POOL_STATES,
         lbaas_settings.POOL_STATES_DICT,
         'POOL_', 'BalancerState'),

        (backup_settings,
         backup_settings.BACKUP_STATES,
         backup_settings.BACKUP_STATES_DICT,
         'BACKUP_STATE_', 'BackupState')
    )

    modules = [gen_module(*args) for args in params]
    modules.extend(gen_module_by_complex_choice())

    choices = (
        ('LoadBalanceProtocol', lbaas_settings.PROTOCOL_CHOICES),
        ('LoadBalanceMethod', lbaas_settings.LB_METHOD_CHOICES),
        ('SessionPersistence', lbaas_settings.SESSION_PER_CHOICES),
        ('MonitorType', lbaas_settings.MONITOR_TYPE),
        ('PatrolItemType', PATROL_ITEM_CATEGORY.CHOICES),
        ('PatrolTaskRepeatType', PATROL_TASK_REPEAT_CHOICE.CHOICES),
        ('MaintItemType', MAINT_ITEM_CATEGORY.CHOICES),
        ('MaintTaskType', MAINT_TASK_CATEGORY.CHOICES),
        ('MaintStepStatus', MAINT_RESULT_STATUS.CHOICES),
        ('PXEStatus', PXE_STATUS.CHOICES),
    )
    return render(request, 'state_service.html',
                  {'modules': modules, 'choices': choices},
                  content_type='application/javascript')


def gen_module(settings, value_labels, stable_dict,
               prefix, module_name, type_=int):

    key_values = []
    length = len(prefix)

    for name in dir(settings):

        if not name.startswith(prefix):
            continue

        value = getattr(settings, name)

        if not isinstance(value, type_):
            continue

        key_values.append((name[length:], value))

    stable_states, unstable_states = [], []

    for state, (_, value) in stable_dict.items():

        if value == 1:
            stable_states.append(state)
        else:
            unstable_states.append(state)

    return {
        'name': module_name,
        'key_values': key_values,
        'value_labels': value_labels,
        'stable_states': stable_states,
        'unstable_states': unstable_states
    }


def gen_module_by_complex_choice():
    """
    key_values: [(label, value), (label, value)] #eg: obj.label=value
    value_labels: ((value, desc), (value, desc)) #eg: django choices
    """
    def _gen(name, complex_choice):
        label_values = [(v, k) for k, v in complex_choice.VALUE_LABELS]
        django_choices = complex_choice.CHOICES
        return {
            'name': name,
            'key_values': label_values,
            'value_labels': django_choices,
            'stable_states': complex_choice.STABLE,
            'unstable_states': complex_choice.UNSTABLE
        }

    result = []
    from devops.machine.settings import PXE_STATUS
    result.append(_gen("PXEStatus", PXE_STATUS))

    from devops.patrol.settings import PATROL_ITEM_STATUS
    result.append(_gen("PatrolItemStatus", PATROL_ITEM_STATUS))

    from devops.patrol.settings import PATROL_TASK_RESULT_STATUS
    result.append(_gen("PatrolItemResultStatus", PATROL_TASK_RESULT_STATUS))

    from devops.maint.settings import MAINT_RESULT_STATUS
    result.append(_gen("MaintResultStatus", MAINT_RESULT_STATUS))

    return result


@login_required
def site_config(request):

    user = request.user
    current_user = {'id': user.id,  'username': user.username}

    if not user.is_superuser:
        # Retrieve user to use some methods of UserProxy
        user = UserProxy.objects.get(pk=user.pk)

        if user.has_udc:
            udc_id = request.session["UDC_ID"]
            data_center = DataCenter.objects.get(userdatacenter__pk=udc_id)
            data_center_name = data_center.name
            rc = create_rc_by_dc(data_center)
            sdn_enabled = neutron.is_neutron_enabled(rc)
        else:
            data_center_name = u'N/A'
            sdn_enabled = False

        current_user['datacenter'] = data_center_name
        current_user['sdn_enabled'] = sdn_enabled
        current_user['has_udc'] = user.has_udc
        current_user['is_approver'] = user.is_approver
        current_user['mobile'] = user.profile.mobile
        current_user['email'] = user.email

    return render(request, 'site_config.js',
                  {'current_user': json.dumps(current_user),
                   'site_config': json.dumps(settings.SITE_CONFIG)},
                  content_type='application/javascript')
