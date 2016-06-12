#-*- coding=utf-8 -*-
import logging
import ast

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from biz.instance.models import Instance
from biz.account.models import Operation
from biz.idc.models import DataCenter
from biz.volume.models import Volume
from biz.backup.models import BackupItem
from biz.workflow.models import Workflow, FlowInstance, ResourceType
from biz.billing.models import Order

from .serializer import VolumeSerializer
from .settings import (VOLUME_STATES_DICT, VOLUME_STATE_ATTACHING,
                       VOLUME_STATE_DETACHING, VOLUME_STATE_AVAILABLE,
                       VOLUME_STATE_DELETING, VOLUME_STATE_ERROR,
                       VOLUME_STATE_IN_USE, VOLUME_STATE_APPLYING)

from cloud.volume_task import volume_create_task, volume_delete_task
from cloud import tasks
from cloud.api import cinder
from cloud.cloud_utils import create_rc_by_dc 
from biz.common.utils import fail, success, error
from biz.account.utils import check_quota

LOG = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
def volume_typelist_view(request):
    try:
        udc_id = request.session["UDC_ID"]
        data_center = DataCenter.objects.get(userdatacenter__pk=udc_id)
        rc = create_rc_by_dc(data_center)
        LOG.info("******** rc is ***********" + str(rc))
        volume_types = cinder.cinderclient(rc).volume_types.list()

        volumetypes = []
        for vt in volume_types:
            LOG.info("******** vt is *********" + str(vt))
             
            volumetypes.append({"name":vt.name})
        #keystone.role_list(rc)
        LOG.info(volumetypes)
        return Response(volumetypes)

    except Exception as e:
        LOG.exception("query volume type list error, msg:[%s]", e)
        return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
def volume_list_view(request):
    try:
        volume_set = Volume.objects.filter(
            deleted=False, user=request.user,
            user_data_center=request.session["UDC_ID"])

        return Response(VolumeSerializer(volume_set, many=True).data)

    except Exception as e:
        LOG.exception("query volume list error, msg:[%s]", e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def volume_list_view_by_instance(request):

    data = request.data
    if data.get('instance_id') is not None:
        volume_set = Volume.objects.filter(
            deleted=False, user=request.user,
            user_data_center=request.session["UDC_ID"],
            instance=data.get('instance_id'))

        serializer = VolumeSerializer(volume_set, many=True)
        return Response(serializer.data)
    else:
        volume_set = Volume.objects.filter(
            deleted=False, user=request.user,
            user_data_center=request.session["UDC_ID"],
            status=VOLUME_STATE_AVAILABLE)
        serializer = VolumeSerializer(volume_set, many=True)
        return Response(serializer.data)


@check_quota(["volume", "volume_size"])
@api_view(['POST'])
def volume_create_view(request):
    try:
        serializer = VolumeSerializer(data=request.data,
                                      context={"request": request})
        if not serializer.is_valid():
            return fail(msg=_('Data is not valid.'),
                        status=status.HTTP_400_BAD_REQUEST)

        pay_type = request.data['pay_type']
        os_volume_type = request.data['os_volume_type']
        os_volume_type = ast.literal_eval(os_volume_type)
        LOG.info("********** os volume type is ************" + str(os_volume_type))
        os_volume_type = os_volume_type['name']
        LOG.info("********** os volume type is ************" + str(os_volume_type))
        pay_num = int(request.data['pay_num'])

        volume = serializer.save()
        Operation.log(volume, obj_name=volume.name, action="create", result=1)
        workflow = Workflow.get_default(ResourceType.VOLUME)

        if settings.SITE_CONFIG['WORKFLOW_ENABLED'] and workflow:

            volume.status = VOLUME_STATE_APPLYING
            volume.save()

            FlowInstance.create(volume, request.user, workflow, None)
            msg = _("Your application for %(size)d GB volume is successful, "
                    "please waiting for approval result!") \
                % {'size': volume.size}
            return success(msg=msg)
        else:
            try:
                volume_create_task.delay(volume, os_volume_type)
                Order.for_volume(volume, pay_type=pay_type, pay_num=pay_num)
                return success(msg=_('Creating volume'),
                               status=status.HTTP_201_CREATED)
            except Exception as e:
                LOG.exception("Failed to create volume, msg: %s", e)
                volume.status = VOLUME_STATE_ERROR
                volume.save()
                return error()
    except Exception as e:
        LOG.exception("create volume error, msg:[%s]", e)
        return error()


@api_view(['POST'])
def volume_update_view(request):
    try:
        data = request.data
        if data.get('id') is not None:
            volume = Volume.objects.get(pk=data.get('id'))
            Operation.log(volume, obj_name=volume.name, action="update", result=1)
            volume.name = data.get('name')
            volume.save()
            return success(msg=_('Volume update success'),
                           status=status.HTTP_201_CREATED)
        else:
            return fail(msg=_('No volume found!'),
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        LOG.exception("Failed to update volume, msg:[%s]", e)
        return error()


@api_view(['POST'])
def volume_action_view(request):
    data = request.data
    action = data.get("action")

    volume = Volume.objects.get(pk=data.get('volume_id'))

    if BackupItem.is_any_unstable(resource=volume):
        return fail(_("This volume has one backup task running now."))

    try:
        if action in ('attach', 'detach'):
            return volume_attach_or_detach(data, volume, action)
        elif 'delete' == action:
            return delete_action(volume)
        return fail(msg=_('Unknown volume action'))
    except Exception as e:
        LOG.exception("Volume action[%s] error, msg:[%s]", action, e)
        return error()


@api_view(['GET'])
def volume_status_view(request):
    return Response(VOLUME_STATES_DICT)


def volume_attach_or_detach(data, volume, action):

    if 'attach' == action:
        instance = Instance.objects.get(pk=data.get('instance_id'))
        volume.change_status(VOLUME_STATE_ATTACHING)

        Operation.log(volume, obj_name=volume.name, action="attach_volume")
        try:
            tasks.attach_volume_to_instance.delay(
                instance=instance, volume=volume)
        except Exception:
            volume.change_status(VOLUME_STATE_AVAILABLE)
            LOG.exception("Attach volume error")
            return error()
        else:
            return success(msg=_('Attaching volume'),
                           status=status.HTTP_201_CREATED)

    elif 'detach' == action:
        volume.change_status(VOLUME_STATE_DETACHING)
        Operation.log(volume, obj_name=volume.name, action="detach_volume")
        try:
            tasks.detach_volume_from_instance.delay(volume)
        except Exception:
            LOG.exception("Detach volume error")
            volume.change_status(VOLUME_STATE_IN_USE)
            return error()
        else:
            return success(msg=_('Detaching volume'),
                           status=status.HTTP_201_CREATED)


def delete_action(volume):
    if volume.instance is not None:
        msg = _('Operation Failed. '
                'Volume %(volume)s is attached to instance: %(instance)s') \
            % {'instance': volume.instance.name, 'volume': volume.name}

        return fail(msg=msg)

    if BackupItem.living.filter(resource_id=volume.id,
                                resource_type=Volume.__name__).exists():
        return fail(_("This volume has backups, please delete them first."))

    if volume.volume_id:
        volume.change_status(VOLUME_STATE_DELETING)

        try:
            volume_delete_task.delay(volume)
            Operation.log(volume, obj_name=volume.name,
                          action="terminate", result=1)
            return success(msg=_('Deleting volume'))
        except Exception:
            LOG.exception("Delete volume error")
            volume.change_status(VOLUME_STATE_ERROR)
            return error()
    else:
        volume.fake_delete()
        return success(msg=_('Volume is deleted.'))
