# -*- coding:utf-8 -*-

from datetime import datetime
import logging
import os

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
from biz.heat.models import Heat 
from biz.heat.serializer import HeatSerializer
from biz.heat.utils import * 
from biz.idc.models import DataCenter, UserDataCenter
from biz.common.pagination import PagePagination
from biz.common.decorators import require_POST, require_GET
from biz.common.utils import retrieve_params, fail
from biz.workflow.models import Step
from cloud.api import keystone
from cloud.tasks import (link_user_to_dc_task, send_notifications,
                         send_notifications_by_data_center, deploy_stack)
from frontend.forms import CloudUserCreateFormWithoutCapatcha

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from biz.image.models import Image

from cloud.cloud_utils import create_rc_by_dc
LOG = logging.getLogger(__name__)


class HeatList(generics.ListAPIView):
    #queryset = Heat.objects.all()
    #serializer_class = HeatSerializer

    def list(self, reqeust):

        datacenter = DataCenter.get_default()
        LOG.info("ccc")
        rc = create_rc_by_dc(datacenter)
        LOG.info("ccc")
        tenants = keystone.keystoneclient(rc).tenants.list()
        LOG.info("cccccccc")
        tenants_id = [] 
        for tenant in tenants:
            if str(tenant.name) not in ["admin", "demo", "services"]:
                tenants_id.append({'tenant_id': tenant.id, 'tenant_name':tenant.name, 'description': tenant.description})
        LOG.info("tenants_id is" + str(tenants_id))
        return Response(tenants_id)


@require_POST
def create_heat(request):
    LOG.info("create_heat")
    try:
        LOG.info(request.data)
        serializer = HeatSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            LOG.info("serializer.is_valid")
            heat = serializer.save()
            LOG.info(heat)
            files = request.data.get('file')
            LOG.info("*** files are " + str(files))
            file_name = files.name
            real_name = file_name.split(".")[0]
            des = '/data/' + str(real_name) + "_" + str(heat.id) + ".template"
            LOG.info("*** des is " + str(des))
            tpl = request.data.get('file').read()
            with open(str(des),"wb+") as destination:
                destination.write(tpl)


            path = des
            filename_ = str(real_name) + "_" + str(heat.id) + ".template"
            real_filename = filename_.split(".")

            heat.file_path = des
            try:
                start_date = request.data['start_date']
                start_time = datetime.strptime(start_date, "%m/%d/%Y").date()
                heat.start_date = start_time
            except:
                pass
            #heat.save()


            user_ids = request.data['ids']
            LOG.info("user_ids are" + str(user_ids))
            LOG.info("user_ids are" + str(type(user_ids)))
            user_ids = str(user_ids)
            user_ids_split = user_ids.split(',')
            LOG.info("user_ids are" + str(user_ids_split))
            for user_id in user_ids:
                LOG.info("*** user_id is ***" + str(user_id))
                stack_name = request.data.get('heatname')
                timeout_mins = 60
                disable_rollback = True
                parameters = []
                template = tpl
                #user_id = request.data.get('user_id')
                heat.user_id = user_id
                meta = {
                   'stack_name': stack_name,
                   'timeout_mins': timeout_mins,
                   'disable_rollback': disable_rollback,
                   #'password': password,
                   'parameters': parameters,
                   'template': template,
                }
                LOG.info("udc is")
                UDC = UserDataCenter.objects.all().filter(user_id=user_id)[0]
                user = User.objects.get(pk=user_id)
                LOG.info("*** template is ***" + str(template))
                LOG.info("*** parameters are ***" + str(parameters))
                password = UDC.keystone_password
                tenant_uuid = None 
                stack = deploy_stack.delay(user, heat, stack_name, timeout_mins, disable_rollback, password, parameters, template, tenant_uuid)

            LOG.info("ccccccccccccccccc")
            return Response(
                {'success': True, "msg": _('部署服务成功！')},
                status='1')

        else:
            return Response({"success": False, "msg": _('发布服务失败 数据无效！'),
                             'errors': serializer.errors},
                             status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create heat, msg:[%s]" % e)
        return Response({"success": False, "msg": _('发布服务失败 异常 未知原因！')})



@api_view(["POST"])
def delete_heats(request):
    try:
        LOG.info("delete_heats")
        ids = request.data.getlist('ids[]')
        LOG.info(ids)
        file_paths = []
        for ID in ids:
            heat = Heat.objects.get(id=ID)
            file_paths.append(heat.file_path)
        LOG.info(file_paths)
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except:
                pass
            #p = subprocess.Popen("os.remove(" + file_path + ")", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        Heat.objects.filter(pk__in=ids).delete()
        return Response({'success': True, "msg": _('删除服务成功！')}, status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Failed to delete heat, msg:[%s]" % e)
        return Response({"success": False, "msg": _('删除服务失败 异常！')})


@api_view(['POST'])
def update_heat(request):
    try:
        LOG.info("update_heat")
        pk = request.data['id']
        LOG.info("---- heat pk is --------" + str(pk))

        heat = Heat.objects.get(pk=pk)
        LOG.info("request.data is" + str(request.data))
        heat.heatname = request.data['heatname']
        heat.description = request.data['description']
        heat.save()
        #Operation.log(heat, heat.name, 'update', udc=heat.udc,
        #              user=request.user)

        return Response(
            {'success': True, "msg": _('Heat is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update heat, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to update heat for unknown reason.')})


@require_GET
def is_heatname_unique(request):
    heatname = request.GET['heatname']
    LOG.info("heatname is" + str(heatname))
    return Response(not Heat.objects.filter(heatname=heatname).exists())




class detail(generics.ListAPIView):

    def list(self, request, tenant_id):
        LOG.info("cccccccccc")
        LOG.info("tenant_id is" + str(tenant_id))

        heat_set = Heat.objects.filter(
            deleted=False, tenant_uuid=tenant_id)
            #user_data_center=request.session["UDC_ID"])
        LOG.info("heat_set is" + str(heat_set))
        """
        data = []
        for h in heat_set:

            deploy_status = ''
            if h.deploy_status:
                LOG.info("ccccccc")
                deploy_status = "发布成功"
            else:
                LOG.info("dddddddd")
                deploy_status = "发布失败"

            LOG.info("aaaaaaaa")
            LOG.info(h.heatname)
            LOG.info(h.description)
            LOG.info(h.file_path)
            LOG.info(deploy_status)
            data.append({'heatname': h.heatname, 'description':h.description, 'file_path': h.file_path, 'deploy_status': deploy_status})
            LOG.info("cccccc")
        """
        serializer = HeatSerializer(heat_set, many=True)
        return Response(serializer.data)

@api_view(["POST"])
def delete_heat(request):

    heat_id = request.data['heat_id']
    heat = Heat.objects.get(pk=heat_id).delete()
    return Response({'success': True, "msg": _('Usergroupers have been deleted!')}, status=status.HTTP_201_CREATED)
