#-*-coding-utf-8-*-

# Author Yang

from datetime import datetime
import logging

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import check_password

from biz.account.settings import QUOTA_ITEM, NotificationLevel
from biz.instance.models import Instance, Flavor
from biz.instance.serializer import InstanceSerializer, FlavorSerializer
from biz.instance.utils import instance_action
from biz.instance.settings import (INSTANCE_STATES_DICT, INSTANCE_STATE_RUNNING,
                                   INSTANCE_STATE_APPLYING, MonitorInterval)
from biz.instancemanage.utils import * 
from biz.idc.models import DataCenter
from biz.common.pagination import PagePagination
from biz.common.decorators import require_POST, require_GET
from biz.common.utils import retrieve_params, fail
from biz.workflow.models import Step
from cloud.tasks import (link_user_to_dc_task, send_notifications, delete_user_instance_network, 
                         send_notifications_by_data_center)
from frontend.forms import CloudUserCreateFormWithoutCapatcha

LOG = logging.getLogger(__name__)


class InstancemanageList(generics.ListCreateAPIView):
    queryset = Instance.objects.all().filter(deleted=False)
    serializer_class = InstanceSerializer

    def list(self, request):
        try:
            serializer = self.serializer_class(self.get_queryset(), many=True)
            LOG.info("********* serializer.data is ********" + str(serializer.data))
            return Response(serializer.data)
        except Exception as e:
            LOG.exception(e)
            return Response()

    def create(self, request, *args, **kwargs):
        raise NotImplementedError()

class InstancemanageDevicePolicy(generics.ListCreateAPIView):

    def list(self, request):
        LOG.info("dddddddddd")
        try:
            devicepolicy = settings.DEVICEPOLICY
            LOG.info("dddddddddd")
            return Response(devicepolicy)
        except Exception as e:
            LOG.exception(e)
            return Response()

    def create(self, request, *args, **kwargs):
        raise NotImplementedError()




@require_POST
def create_instancemanage(request):

    try:
        serializer = InstancemanageSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Instancemanage is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Instancemanage data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:

        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create instancemanage for unknown reason.')})



@api_view(["POST"])
def delete_instancemanages(request):
    ids = request.data.getlist('ids[]')
    Instancemanage.objects.filter(pk__in=ids).delete()
    return Response({'success': True, "msg": _('Instancemanages have been deleted!')}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def update_instancemanage(request):
    try:

        pk = request.data['id']
        LOG.info("---- instancemanage pk is --------" + str(pk))

        instancemanage = Instancemanage.objects.get(pk=pk)
        LOG.info("ddddddddddddd")
        LOG.info("request.data is" + str(request.data))
        instancemanage.instancemanagename = request.data['instancemanagename']

        LOG.info("dddddddddddd")
        instancemanage.save()
        #Operation.log(instancemanage, instancemanage.name, 'update', udc=instancemanage.udc,
        #              user=request.user)

        return Response(
            {'success': True, "msg": _('Instancemanage is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update instancemanage, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to update instancemanage for unknown reason.')})


@require_GET
def is_instancemanagename_unique(request):
    instancemanagename = request.GET['instancemanagename']
    LOG.info("instancemanagename is" + str(instancemanagename))
    return Response(not Instancemanage.objects.filter(instancemanagename=instancemanagename).exists())

@require_POST
def devicepolicyupdate(request):
    LOG.info("*** request.data is ***"  + str(request.data))
    role = request.data['role']
    instance_id = request.data['id']
    role_str = str(role)
    role_list = []
    if ',' not in role_str:
        role_list.append(role_str)
    else:
        role_list = role_str.split(",")
    LOG.info("********** role_list is **********" + str(role_list))
    LOG.info("********** instance_id  is **********" + str(instance_id))
    if "usb" in role_list:
        for role in role_list:
            LOG.info("*** role is ****" + str(role))


            instance = Instance.objects.get(pk=instance_id)
            instance.policy = 1 
            instance.save()
    return Response({"success": True, "msg": _(
           'Sucess.')})

@require_POST
def devicepolicyundo(request):
    LOG.info("*** request.data is ***"  + str(request.data))
    instance_id = None
    for key, value in request.data.items():
        instance_id = value
    LOG.info("********** instance_id  is **********" + str(instance_id))
    instance = Instance.objects.get(pk=instance_id)
    instance.policy = 0 
    instance.save()
    return Response({"success": True, "msg": _(
           'Sucess.')})

@require_POST
def delete_instance(request):
    LOG.info("*** request.data is ***"  + str(request.data))
    instance_id = None
    for key, value in request.data.items():
        instance_id = value
    LOG.info("********** instance_id  is **********" + str(instance_id))
    instance = Instance.objects.get(pk=instance_id)
    instance_id = instance.uuid
    LOG.info("********** instance_id  is **********" + str(instance_id))
    try:
        delete_user_instance_network(request, instance_id)
    except:
        pass
    instance.deleted = True
    instance.save()
    return Response({"success": True, "msg": _(
           'Sucess.')})
