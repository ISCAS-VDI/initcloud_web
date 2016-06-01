#-*-coding-utf-8-*-

import logging

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from biz.account.models import Contract, UserProxy
from biz.idc.models import DataCenter
from biz.idc.serializer import DataCenter, DataCenterSerializer
from biz.instance.models import Instance, Flavor
from biz.image.models import Image

from cloud.tasks import hypervisor_stats_task


LOG = logging.getLogger(__name__)


@api_view(["GET"])
def summary(request):
    return Response({"user_num": User.objects.filter(is_superuser=False).count(),
                     "instance_num": Instance.objects.filter(deleted=False).count(),
                     "flavor_num": Flavor.objects.count(),
                     "data_center_num": DataCenter.objects.count(),
                     "contract_num": Contract.objects.filter(deleted=False).count(),
                     "image_num": Image.objects.count()})


@api_view(["POST"])
def init_data_center(request):

    params = {'name': request.data['name']}

    for key in ('host', 'project', 'user', 'password', 'auth_url', 'ext_net'):
        params[key] = request.data[key]

    try:
        data_center = DataCenter.objects.create(**params)
    except IntegrityError:
        return Response({'success': False,
                        "msg": _('The host IP is used by other Data Center, Please check your host IP.')},
                        status=status.HTTP_200_OK)
    except Exception as e:
        LOG.error("Failed to create data center, msg:[%s]" % e)
        return Response({'success': False,
                        "msg": _("Unknown Error happened when creating data center!"),
                        "resouce": "data_center"},
                        status=status.HTTP_200_OK)
    else:
        return Response({
            "success": True,
            'data': DataCenterSerializer(data_center).data,
            "msg": _("Data center is initialized successfully!")
        })


@api_view(['POST'])
def init_flavors(request):

    data = request.data
    names = data.getlist('names[]')
    cpus = data.getlist('cpus[]')
    memories = data.getlist('memories[]')
    prices = data.getlist('prices[]')

    try:
        for i in range(len(names)):
            Flavor.objects.create(name=names[i], cpu=cpus[i],
                                  memory=memories[i], price=prices[i])
    except Exception as e:
        LOG.error("Failed to create flavors, msg:[%s]" % e)
        return Response({'success': False,
                        "msg": _("Unknown Error happened when creating flavors!")},
                        status=status.HTTP_200_OK)
    else:
        return Response({"success": True, "msg": _("Flavors are initialized successfully!")})


@api_view(['POST'])
def init_images(request):

    data = request.data

    names = data.getlist('names[]')
    login_names = data.getlist('login_names[]')
    uuids = data.getlist('uuids[]')
    os_types = data.getlist('os_types[]')
    disk_sizes = data.getlist('disk_sizes[]')

    data_center = DataCenter.get_default()

    try:
        for i in range(len(names)):
            Image.objects.create(name=names[i], login_name=login_names[i],
                                 uuid=uuids[i], os_type=os_types[i],
                                 data_center=data_center,
                                 disk_size=disk_sizes[i])
    except Exception as e:
        LOG.exception("Failed to create images")
        return Response({'success': False,
                         "msg": _("Unknown Error happened when creating images!")},
                        status=status.HTTP_200_OK)
    else:
        return Response({"success": True,
                         "msg": _("Images are initialized successfully!")})


@api_view(['GET'])
def hypervisor_stats(request):

    user = request.user
    user_ = UserProxy.objects.get(pk=user.pk)
    
    if request.user.is_superuser or user_.is_system_user or user_.is_safety_user or user_.is_audit_user:
        data_center = DataCenter.get_default()
        stats = hypervisor_stats_task(data_center)
        if stats: 
            result = {
                "vcpus": stats.vcpus,
                "vcpus_used": stats.vcpus_used,
                "memory_mb": stats.memory_mb,
                "memory_mb_used": stats.memory_mb_used,
                "local_gb": stats.local_gb,
                "local_gb_used": stats.local_gb_used,
            } 
            return Response({"success": True, "stats": result})
        else:
            return Response({"success": False,
                             "msg": _("Hypervisor status is none.")})
    else:
        return Response({
            "success": False,
            "msg": _("Only super user can view the hypervisor status.")})
