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
from biz.group.models import Group 
from biz.group.serializer import GroupSerializer
from biz.group.utils import * 
from biz.idc.models import DataCenter
from biz.common.pagination import PagePagination
from biz.common.decorators import require_POST, require_GET
from biz.common.utils import retrieve_params, fail
from biz.workflow.models import Step
from cloud.tasks import (link_user_to_dc_task, send_notifications,
                         send_notifications_by_data_center)
from frontend.forms import CloudUserCreateFormWithoutCapatcha

LOG = logging.getLogger(__name__)


class GroupList(generics.ListAPIView):
    LOG.info("--------- I am group list in GroupList ----------")
    queryset = Group.objects.all()
    LOG.info("--------- Queryset is --------------" + str(queryset)) 
    serializer_class = GroupSerializer



@require_POST
def create_group(request):

    try:
        serializer = GroupSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Group is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Group data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:

        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create group for unknown reason.')})



@api_view(["POST"])
def delete_groups(request):
    ids = request.data.getlist('ids[]')
    Group.objects.filter(pk__in=ids).delete()
    return Response({'success': True, "msg": _('Groups have been deleted!')}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def update_group(request):
    try:

        pk = request.data['id']
        LOG.info("---- group pk is --------" + str(pk))

        group = Group.objects.get(pk=pk)
        LOG.info("ddddddddddddd")
        LOG.info("request.data is" + str(request.data))
        group.groupname = request.data['groupname']

        LOG.info("dddddddddddd")
        group.save()
        #Operation.log(group, group.name, 'update', udc=group.udc,
        #              user=request.user)

        return Response(
            {'success': True, "msg": _('Group is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update group, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to update group for unknown reason.')})


@require_GET
def is_groupname_unique(request):
    groupname = request.GET['groupname']
    LOG.info("groupname is" + str(groupname))
    return Response(not Group.objects.filter(groupname=groupname).exists())
