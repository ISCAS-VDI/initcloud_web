from rest_framework.response import Response

from biz.common.decorators import require_GET, require_POST

@require_GET
def vdstatus(request):
    data = []
    data.append({"username": "abc", "vm": "ddc", "status": "online"})
    return Response(data)

