from django.conf import settings

from rest_framework.response import Response
from rest_framework import generics

from biz.common.decorators import require_GET, require_POST
from biz.common.pagination import PagePagination
from biz.vir_desktop.serializer import VDStatusSerializer

data = []
for i in range(25):
    data.append({"username": "abc"+str(i), "vm": "ddc"+str(i)})

class VDStatusList(generics.ListAPIView):
    # TODO: get data from webservice settings.MGR_HTTP_ADDR
    queryset = data
    serializer_class = VDStatusSerializer
    pagination_class = PagePagination

