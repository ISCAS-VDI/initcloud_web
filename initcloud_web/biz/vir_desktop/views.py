# -*- coding: utf-8 -*-
from django.conf import settings
import requests, logging

from rest_framework.response import Response
from rest_framework import generics

from biz.common.decorators import require_GET, require_POST
from biz.common.pagination import PagePagination
from biz.vir_desktop.serializer import VDStatusSerializer

LOG = logging.getLogger(__name__)

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

