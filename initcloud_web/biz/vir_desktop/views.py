from rest_framework.response import Response
from rest_framework import generics

from biz.common.decorators import require_GET, require_POST
from biz.common.pagination import PagePagination
from biz.vir_desktop.serializer import VDStatusSerializer

data = []
for i in range(25):
    data.append({"username": "abc"+str(i), "vm": "ddc"+str(i)})

@require_GET
def vdstatus(request):
    rsp = {
        "results": data,
        "count": 25
    }
    return Response(rsp)

class VDStatusList(generics.ListAPIView):
    queryset = data
    serializer_class = VDStatusSerializer
    pagination_class = PagePagination

