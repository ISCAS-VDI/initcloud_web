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
from biz.role.models import Role 
from biz.role.serializer import RoleSerializer
from biz.role.utils import * 
from biz.idc.models import DataCenter
from biz.common.pagination import PagePagination
from biz.common.decorators import require_POST, require_GET
from biz.common.utils import retrieve_params, fail
from cloud.cloud_utils import get_nova_admin
from biz.workflow.models import Step
from cloud.tasks import (role_create, role_delete, send_notifications,
                         send_notifications_by_data_center)
from frontend.forms import CloudUserCreateFormWithoutCapatcha

LOG = logging.getLogger(__name__)


class RoleList(generics.ListAPIView):
    LOG.info("--------- I am role list in RoleList ----------")
    queryset = Role.objects.all()
    LOG.info("--------- Queryset is --------------" + str(queryset)) 
    serializer_class = RoleSerializer



@require_POST
def create_role(request):



    try:

        rolename = request.data.get('rolename')
        LOG.info("*********** start to create role in openstack  role name is ***********" + str(rolename))
        created_role = role_create(request, rolename)
        LOG.info("************* create success **********")
    except:
        return False

    LOG.info("---------- data is -----------" + str(request.data))
    try:
        serializer = RoleSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Role is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Role data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:

        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create role for unknown reason.')})

@api_view(["POST"])
def delete_roles(request):
    ids = request.data.getlist('ids[]')
    LOG.info("******** ids are **********" + str(ids))
    for id_ in ids:
        role = Role.objects.get(pk=int(id_))
        rolename = role.rolename 
        LOG.info("*********** rolename *********" + str(rolename))
        role_delete_keystone = role_delete(request, rolename)
    Role.objects.filter(pk__in=ids).delete()
    return Response({'success': True, "msg": _('Roles have been deleted!')}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def update_role(request):
    try:

        pk = request.data['id']
        LOG.info("---- role pk is --------" + str(pk))

        role = Role.objects.get(pk=pk)
        LOG.info("ddddddddddddd")
        LOG.info("request.data is" + str(request.data))
        role.rolename = request.data['rolename']

        LOG.info("dddddddddddd")
        role.save()
        #Operation.log(role, role.name, 'update', udc=role.udc,
        #              user=request.user)

        return Response(
            {'success': True, "msg": _('Role is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update role, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to update role for unknown reason.')})


@require_GET
def is_rolename_unique(request):
    rolename = request.GET['rolename']
    LOG.info("rolename is" + str(rolename))
    return Response(not Role.objects.filter(rolename=rolename).exists())
