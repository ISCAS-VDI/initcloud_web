# -*- coding: utf-8 -*-
from django.conf import settings
import requests, logging, time

from rest_framework.response import Response
from rest_framework import generics

from biz.common.decorators import require_GET, require_POST
from biz.common.pagination import PagePagination
from biz.vir_desktop.serializer import VDStatusSerializer
from biz.vir_desktop.models import VirDesktopAction

import cloud.software_mgr_task as mgr

LOG = logging.getLogger(__name__)

# data for testing
data = []
for i in range(25):
    data.append({"user": "abc"+str(i), "vm": "ddc"+str(i), "ip_addr": "1.1.1."+str(i)})

class VDStatusList(generics.ListAPIView):
    # queryset = data
    serializer_class = VDStatusSerializer
    pagination_class = PagePagination
    
    def get_queryset(self):
        LOG.info("---vir_desktop.views---")
        ret = []
        try:
            r = requests.get(settings.MGR_HTTP_ADDR)
            if r.status_code == 200:
              ret = r.json()
              LOG.info(ret)
            else:
              ret = [{"user": "Error code: "+str(r.status_code), "vm": "null"}]
        except Exception, e:
            LOG.info(e)
        
        return ret

@require_GET
def software_can_setup(request):
    # Use the API to get corresponding data
    return Response(mgr.get_available_software())

@require_GET
def software_can_remove(request):
    addr = request.query_params.get("addr")
    # Use the API to get corresponding data
    return Response(mgr.get_installed_software(addr))

@require_POST
def software_setup(request):
    LOG.info(request.data)
    try:
        rsp = { "success": True, "msg": "Setup OK" }
        users = request.data.getlist("users[]")
        vms = request.data.getlist("vms[]")
        ip_addrs = request.data.getlist("ip_addrs[]")
        softwares = request.data.getlist("softwares[]")
        # Add a log in auditor DB and the status is setuping
        action_ids = []
        for vm in vms:
            action = VirDesktopAction(vm_id=vm, state='setuping')
            action.save()
            LOG.info("action id: %s" % action.id)
            action_ids.append(action.id)
        rsp["ids"] = action_ids
        # Use the API to setup softwares
        ares = mgr.install_software.delay(action_ids, ip_addrs, softwares)
    except Exception, e:
        LOG.info("---software_setup---: %s" % e)
        rsp["success"] = False
        rsp["msg"] = e

    return Response(rsp)

@require_POST
def software_remove(request):
    try:
        rsp = { "success": True, "msg": "Remove OK" }
        users = request.data.getlist("users[]")
        vms = request.data.getlist("vms[]")
        ip_addrs = request.data.getlist("ip_addrs[]")
        softwares = request.data.getlist("softwares[]")
        # Add a log in auditor DB and the status is removing
        action_ids = []
        for vm in vms:
            action = VirDesktopAction(vm_id=vm, state='removing')
            action.save()
            LOG.info("action id: %s" % action.id)
            action_ids.append(action.id)
        rsp["ids"] = action_ids
        # Use the API to Remove softwares
        mgr.uninstall_software.delay(action_ids, ip_addrs, softwares)
    except Exception, e:
        LOG.info("---software_remove---: %s" % e)
        rsp["success"] = False
        rsp["msg"] = e

    return Response(rsp)

# API to trace status
@require_GET
def action_status(request):
    action_id = request.query_params.get("vm")
    # product_id = request.query_params.get("product")
    try:
        action = VirDesktopAction.objects.filter(id=action_id)
        LOG.info("---%d %s %s---" % (len(action), action[0].create_date, action[0].state))
        if len(action) > 0:
            return Response({'status': action[0].state})
    except Exception, e:
        LOG.info("Action status error: %s" % e)
        return Response({'success': False})

