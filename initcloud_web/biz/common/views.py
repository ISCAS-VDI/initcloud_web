#!/usr/bin/env python
# coding=utf-8

import json
import logging

from django.conf import settings
from django.shortcuts import render
from rest_framework import permissions
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication 

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

    choices = (
        ('LoadBalanceProtocol', lbaas_settings.PROTOCOL_CHOICES),
        ('LoadBalanceMethod', lbaas_settings.LB_METHOD_CHOICES),
        ('SessionPersistence', lbaas_settings.SESSION_PER_CHOICES),
        ('MonitorType', lbaas_settings.MONITOR_TYPE)
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


@login_required
def site_config(request):


    user = request.user

    user_ = UserProxy.objects.get(pk=user.pk)

    current_user = {'username': user.username, 'is_system_user': user_.is_system_user, 'is_safety_user': user_.is_safety_user, 'is_audit_user': user_.is_audit_user}


    if user_.is_system_user:
        return render(request, 'site_config.js',
                      {'current_user': json.dumps(current_user),
                       'site_config': json.dumps(settings.SITE_CONFIG)},
                      content_type='application/javascript')
    if user_.is_audit_user:
        return render(request, 'site_config.js',
                      {'current_user': json.dumps(current_user),
                       'site_config': json.dumps(settings.SITE_CONFIG)},
                      content_type='application/javascript')

    if user_.is_safety_user:
        return render(request, 'site_config.js',
                      {'current_user': json.dumps(current_user),
                       'site_config': json.dumps(settings.SITE_CONFIG)},
                      content_type='application/javascript')


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

class IsAuditUser(permissions.BasePermission):
    """
    Object-level permission to only allow system users of an object to edit it.
    Assumes the user model instance has an is_system_user attribute.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.has_perm("workflow.audit_user"):
            return True 

    def has_object_permission(self, request, view, obj):
        return False 

class IsSafetyUser(permissions.BasePermission):
    """
    Object-level permission to only allow system users of an object to edit it.
    Assumes the user model instance has an is_system_user attribute.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.has_perm("workflow.safety_user"):
            return True 

    def has_object_permission(self, request, view, obj):
        return False 

class IsSystemUser(permissions.BasePermission):
    """
    Object-level permission to only allow system users of an object to edit it.
    Assumes the user model instance has an is_system_user attribute.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.has_perm("workflow.system_user"):
            return True 

    def has_object_permission(self, request, view, obj):
        return False 

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

