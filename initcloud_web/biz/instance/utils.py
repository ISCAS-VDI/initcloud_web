#-*- coding=utf-8 -*-

import logging

from django.utils.translation import ugettext_lazy as _

from biz.account.models import Operation
from biz.backup.models import BackupItem
from biz.instance.models import Instance
from biz.instance.settings import (ALLOWED_INSTANCE_ACTIONS,
                                   INSTANCE_ACTION_NEXT_STATE)
from cloud.cloud_utils import create_rc_by_instance
from biz.billing.models import Order

from cloud.tasks import (instance_status_synchronize_task,
                         instance_get_vnc_console, )
from cloud.api import nova

OPERATION_SUCCESS = 1
OPERATION_FAILED = 0
OPERATION_FORBID = 2

LOG = logging.getLogger(__name__)


def get_instance_vnc_console(instance):
    vnc = instance_get_vnc_console(instance) 
    if vnc and vnc.url:
        return {"OPERATION_STATUS": OPERATION_SUCCESS,
                "vnc_url": "%s&instance_name=%s(%s)" % (
                    vnc.url, instance.name, instance.uuid)}
    else:
        return {"OPERATION_STATUS": OPERATION_FAILED}


def _server_reboot(rc, instance):
    if instance.uuid:
        nova.server_reboot(rc, instance.uuid)
    return True


def _server_delete(rc, instance):
    if instance.uuid:
        try:
            nova.server_delete(rc, instance.uuid) 
        except nova.nova_exceptions.NotFound:
            pass
    return True


def _server_start(rc, instance):
    if instance.uuid:
        nova.server_start(rc, instance.uuid)
    return True


def _server_stop(rc, instance):
    if instance.uuid:
        nova.server_stop(rc, instance.uuid)
    return True


def _server_unpause(rc, instance):
    if instance.uuid:
        nova.server_unpause(rc, instance.uuid)
    return True


def _server_pause(rc, instance):
    if instance.uuid:
        nova.server_pause(rc, instance.uuid)
    return True


def instance_action(user, instance_id, action):
    if action not in ALLOWED_INSTANCE_ACTIONS.keys():
        return {"OPERATION_STATUS": OPERATION_FAILED,
                "status": "Unsupported action [%s]" % action}
    #instance = Instance.objects.get(pk=instance_id, user=user, deleted=False)
    instance = Instance.objects.get(pk=instance_id, deleted=False)
    # restoring instance can't do any action!

    if BackupItem.is_any_restoring(instance):
        return {"OPERATION_STATUS": OPERATION_FORBID,
                "MSG": _("Cannot operate this instance because it's in "
                         "restore process."),
                "status": instance.status}

    if action in ('reboot', 'power_on'):
        for volume in instance.volume_set.all():

            if BackupItem.is_any_restoring(volume):
                return {"OPERATION_STATUS": OPERATION_FAILED,
                        "MSG": _("Cannot operate this instance because "
                                 "one volume attached to it is in "
                                 "restore process."),
                        "status": instance.status}

    if action == 'terminate' and \
        BackupItem.living.filter(
            resource_id=instance.id,
            resource_type=Instance.__name__).exists():

        return {"OPERATION_STATUS": OPERATION_FAILED,
                "MSG": _("This instance have backup chains, please delete "
                         "these first."),
                "status": instance.status}

    if action == 'terminate':
        Order.disable_order_and_bills(instance)

    Operation.log(instance, obj_name=instance.name, action=action)
    
    if action == "vnc_console":
        return get_instance_vnc_console(instance)

    _ACTION_MAPPING = {
        "reboot": _server_reboot,
        "terminate": _server_delete,
        "power_on": _server_start,
        "power_off": _server_stop,
        "restore": _server_unpause,
        "pause": _server_pause,
    }

    try:
        rc = create_rc_by_instance(instance)
        act = _ACTION_MAPPING.get(action)
        act(rc, instance)
        instance.status = INSTANCE_ACTION_NEXT_STATE[action]
        instance.save()
        instance_status_synchronize_task.delay(instance, action)
    except Exception as ex:
        LOG.exception("Instance action [%s] raise exception, [%s].",
                            action, instance)
        return {"OPERATION_STATUS": OPERATION_FAILED, 
                "status": "%s" % ex.message}
    else: 
        return {"OPERATION_STATUS": OPERATION_SUCCESS, "status": instance.status}
