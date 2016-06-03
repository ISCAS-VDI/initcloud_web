# -*- coding: utf-8 -*-
from django.conf import settings
import requests, logging

from rest_framework.response import Response
from rest_framework import generics

from biz.common.decorators import require_GET, require_POST
from biz.common.pagination import PagePagination
from biz.vir_desktop.serializer import VDStatusSerializer

# TODO: import software mgr client

LOG = logging.getLogger(__name__)

# data for testing
data = []
for i in range(25):
    data.append({"user": "abc"+str(i), "vm": "ddc"+str(i)})

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

# data for testing
soft_list = []
for i in range(20):
    soft_list.append({"name": "software" + str(i)})

@require_GET
def software_can_setup(request):
    # TODO: Use the API to get corresponding data
    return Response(soft_list)

@require_GET
def software_can_remove(request):
    # TODO: Use the API to get corresponding data
    return Response(soft_list)

@require_POST
def software_setup(request):
    LOG.info(request.data)
    try:
        rsp = { "success": True, "msg": "Setup OK" }
        users = request.data.getlist("users[]")
        vms = request.data.getlist("vms[]")
        softwares = request.data.getlist("softwares[]")
        # TODO: Use the API to setup softwares
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
        softwares = request.data.getlist("softwares[]")
        # TODO: Use the API to Remove softwares
    except Exception, e:
        LOG.info("---software_remove---: %s" % e)
        rsp["success"] = False
        rsp["msg"] = e

    return Response({
        "success": True,
        "msg": "Remove OK"
    })

