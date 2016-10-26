#coding=utf-8

import re
import logging
import os
from bson import json_util
import subprocess
import uuid
from djproxy.views import HttpProxy
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (api_view,
                                       authentication_classes,
                                       permission_classes)

from biz.volume.models import Volume
from biz.volume.serializer import VolumeSerializer
from biz.firewall.models import Firewall
from biz.firewall.serializer import FirewallSerializer
from biz.idc.models import UserDataCenter, DataCenter

from biz.instance.models import Instance, Flavor
from biz.instance.serializer import InstanceSerializer, FlavorSerializer
from biz.instance.utils import instance_action
from biz.instance.settings import (INSTANCE_STATES_DICT, INSTANCE_STATE_RUNNING,
                                   INSTANCE_STATE_APPLYING, MonitorInterval)
from biz.billing.models import Order
from biz.account.utils import check_quota
from biz.account.models import Operation
from biz.workflow.models import Workflow, FlowInstance
from biz.workflow.settings import ResourceType
from biz.network.models import Network

from biz.common.decorators import require_GET, require_POST
from django.views.decorators.http import require_POST as django_POST
from cloud.instance_task import (instance_create_task,
                                instance_get_console_log,
                                instance_get, instance_get_port)

from keystoneclient.v2_0 import client
from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient.client import Client
from biz.common.views import IsSystemUser, IsAuditUser, IsSafetyUser
from cloud.cloud_utils import get_nova_admin
import traceback


from django.db.models import Q

LOG = logging.getLogger(__name__)
OPERATION_SUCCESS = 1
OPERATION_FAILED = 0


class InstanceList(generics.ListCreateAPIView):
    queryset = Instance.objects.all().filter(deleted=False)
    serializer_class = InstanceSerializer
    #LOG.info(Instance.objects.all())
    def list(self, request):
        try:
            udc_id = request.session["UDC_ID"]
            UDC = UserDataCenter.objects.all().filter(user=request.user)[0]
            project_id = UDC.tenant_uuid
            queryset = self.get_queryset().filter(
                Q(user=request.user, user_data_center__pk=udc_id) | Q(tenant_uuid=project_id))
            serializer = InstanceSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            LOG.exception(e)
            return Response()

    def create(self, request, *args, **kwargs):
        raise NotImplementedError()


class InstanceDetail(generics.RetrieveAPIView):
    queryset = Instance.objects.all().filter(deleted=False)
    serializer_class = InstanceSerializer

    def get(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            if obj and obj.user == request.user:
                serializer = InstanceSerializer(obj)
                return Response(serializer.data)
            else:
                raise
        except Exception as e:
            LOG.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)


class FlavorList(generics.ListCreateAPIView):
    queryset = Flavor.objects.all()
    serializer_class = FlavorSerializer

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)


class FlavorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Flavor.objects.all()
    serializer_class = FlavorSerializer


def get_nova_admin(request):
    auth = v2.Password(auth_url=settings.AUTH_URL,
			username = settings.ADMIN_NAME,
			password = settings.ADMIN_PASS,
			tenant_name = settings.ADMIN_TENANT_NAME)
    sess = session.Session(auth=auth)
    novaClient = Client(settings.NOVA_VERSION, session = sess)
    return novaClient

@api_view(["POST"])
def create_flavor(request):
    try:
        serializer = FlavorSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
	    #LOG.info(serializer.data)
	    LOG.info("************ CREATE FLAVOR ***************")
	    novaadmin = get_nova_admin(request)
	    #LOG.info(type(novaadmin))
	    #LOG.info(novaadmin)
	    #LOG.info(novaadmin.flavors.list())
	    mem = request.data.get("memory")
	    name = request.data.get("name")
	    cpu = request.data.get("cpu")
	    disk = request.data.get("disk")
	    flavor = novaadmin.flavors.create(name = name , ram = mem, vcpus = cpu, disk = disk)
	    #LOG.info(flavor.id)
	    flavorid = flavor.id
	    try:
	    	serializer.save(flavorid = flavor.id)
	    except:
		traceback.print_exc()
	    LOG.info(Flavor.objects.all().filter(flavorid = flavor.id))
	    
            return Response({'success': True, "msg": _('Flavor is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Flavor data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create flavor for unknown reason.')})


@api_view(["POST"])
def update_flavor(request):
    try:
        flavor = Flavor.objects.get(pk=request.data['id'])
        serializer = FlavorSerializer(instance=flavor, data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Flavor is updated successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Flavor data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to update flavor for unknown reason.')})


@api_view(["POST"])
def delete_flavors(request):
    ids = request.data.getlist('ids[]')
    flavorid = Flavor.objects.get(pk__in=ids).flavorid
    novaadmin = get_nova_admin(request)
    #novaadmin.flavors.delete(flavorid)
    try:
	novaadmin.flavors.delete(flavorid)
    except:
	traceback.print_exc()
    Flavor.objects.filter(pk__in=ids).delete()
    return Response({'success': True, "msg": _('Flavors have been deleted!')}, status=status.HTTP_201_CREATED)


@check_quota(["instance", "vcpu", "memory"])
@api_view(["POST"])
def instance_create_view(request):
    count = request.DATA.get("instance", u"1")
    try:
        count = int(count)
    except:
        count = 1

    user_id = request.user.id
    LOG.info("** user_id is ***" + str(user_id))
    user_data_center = UserDataCenter.objects.filter(user__id=request.user.id)[0]
    LOG.info("*** user_data_center ***" + str(user_data_center))
    user_tenant_uuid = user_data_center.tenant_uuid
    LOG.info("*** user_tenant_uuid is ***" + str(user_tenant_uuid))

    pay_type = request.data['pay_type']
    pay_num = int(request.data['pay_num'])

    if count > settings.BATCH_INSTANCE:
        return Response({"OPERATION_STATUS": OPERATION_FAILED},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    network_id = request.DATA.get("network_id", u"0")
    try:
        network = Network.objects.get(pk=network_id)
    except Network.DoesNotExist:
        pass
    else:
        # VLAN mode: we do not have to add router to network.
        if settings.VLAN_ENABLED == False:
            if not network.router:
                msg = _("Your selected network has not linked to any router.")
                return Response({"OPERATION_STATUS": OPERATION_FAILED,
                               "msg": msg}, status=status.HTTP_409_CONFLICT)


    has_error, msg = False, None
    for i in range(count):
        serializer = InstanceSerializer(data=request.data, context={"request": request}) 
        if serializer.is_valid():
            name = request.DATA.get("name", "Server")
            if i > 0:
                name = "%s-%04d" % (name, i)
            ins = serializer.save(name=name)

            Operation.log(ins, obj_name=ins.name, action="launch", result=1)
            workflow = Workflow.get_default(ResourceType.INSTANCE)

            if settings.SITE_CONFIG['WORKFLOW_ENABLED'] and workflow:
                ins.status = INSTANCE_STATE_APPLYING
                ins.save()

                FlowInstance.create(ins, request.user, workflow, request.DATA['password'])
                msg = _("Your application for instance \"%(instance_name)s\" is successful, "
                        "please waiting for approval result!") % {'instance_name': ins.name}
            else:
                instance_create_task.delay(ins, password=request.DATA["password"],user_tenant_uuid=user_tenant_uuid)
                Order.for_instance(ins, pay_type=pay_type, pay_num=pay_num)
                msg = _("Your instance is created, please wait for instance booting.")
        else:
            has_error = True
            break

    if has_error: 
        return Response({"OPERATION_STATUS": OPERATION_FAILED},
                        status=status.HTTP_400_BAD_REQUEST) 
    else:
        return Response({"OPERATION_STATUS": OPERATION_SUCCESS,
                          "msg": msg}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def instance_action_view(request, pk):
    instance_id, action = request.data['instance'], request.data['action']
    data = instance_action(request.user, instance_id, action)
    return Response(data)


@api_view(["GET"])
def instance_status_view(request):
    return Response(INSTANCE_STATES_DICT)


@api_view(["GET"])
def instance_search_view(request):

    UDC = UserDataCenter.objects.all().filter(user=request.user)[0]
    project_id = UDC.tenant_uuid
    instance_set = Instance.objects.filter(Q(deleted=False, user=request.user, status=INSTANCE_STATE_RUNNING,
        user_data_center=request.session["UDC_ID"]) | Q(tenant_uuid=project_id))
    serializer = InstanceSerializer(instance_set, many=True)
    return Response(serializer.data)

### TODO: remove below two API for qos


def qos_get_instance_detail(instance):
    instance_data = InstanceSerializer(instance).data

    try:
        server = instance_get(instance)
        instance_data['host'] = getattr(server, 'OS-EXT-SRV-ATTR:host', None)
        instance_data['instance_name'] = getattr(server,
                                'OS-EXT-SRV-ATTR:instance_name', None)
    except Exception as e:
        LOG.error("Obtain host fail,msg: %s" % e)
    try:
        ports = instance_get_port(instance)
        if ports:
            instance_data['port'] = ports[0].port_id
        else:
            instance_data['port'] = False
    except Exception as e:
        LOG.error("Obtain instance port fail,msg: %s" % e)

    try:
        from biz.floating.models import Floating
        floating = Floating.get_instance_ip(instance.id)
        if floating:
            instance_data["bandwidth"] = floating.bandwidth
        else:
            instance_data["bandwidth"] = settings.DEFAULT_BANDWIDTH
    except Exception as e:
        LOG.error("Obtain instance bandwidth fail,msg: %s" % e)

    return instance_data


@require_GET
@authentication_classes([])
@permission_classes([])
def instance_detail_view_via_uuid_or_ip(request, uuid_or_ip):
    instance_uuid = -1
    try:
        instance_uuid = uuid.UUID(uuid_or_ip) 
    except:
        pass

    try:
        if uuid_or_ip.count(".") == 3:
            from biz.floating.models import Floating
            floatings = Floating.objects.filter(ip=uuid_or_ip,
                                        deleted=False)
            if floatings.exists():
                if floatings[0].resource_type == "INSTANCE":
                    instance_uuid = Instance.objects.get(
                             pk=floatings[0].resource).uuid
    except:
        pass

    try:
        instance = Instance.objects.get(uuid=instance_uuid)
    except Instance.DoesNotExist:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    return Response(qos_get_instance_detail(instance))

### remove below two API for qos end


@api_view(["GET"])
def instance_detail_view(request, pk):
    tag = request.GET.get("tag", 'instance_detail')
    try:
        #instance = Instance.objects.get(pk=pk, user=request.user)
        instance = Instance.objects.get(pk=pk)
    except Exception as e:
        LOG.error("Get instance error, msg:%s" % e)
        return Response({"OPERATION_STATUS": 0, "MSG": "Instance no exist"}, status=status.HTTP_200_OK)

    if "instance_detail" == tag:
        return _get_instance_detail(instance)
    elif 'instance_log' == tag:
        log_data = instance_get_console_log(instance)
        return Response(log_data)


def _get_instance_detail(instance):

    instance_data = InstanceSerializer(instance).data

    try:
        server = instance_get(instance)
        instance_data['host'] = getattr(server, 'OS-EXT-SRV-ATTR:host', None)
        instance_data['instance_name'] = getattr(server,
                                'OS-EXT-SRV-ATTR:instance_name', None)
        instance_data['fault'] = getattr(server, 'fault', None)

    except Exception as e:
        LOG.error("Obtain host fail,msg: %s" % e)

    try:
        firewall = Firewall.objects.get(pk=instance.firewall_group.id)
        firewall_data = FirewallSerializer(firewall).data
        instance_data['firewall'] = firewall_data
    except Exception as e:
        LOG.exception("Obtain firewall fail, msg:%s" % e)

    # 挂载的所有硬盘
    volume_set = Volume.objects.filter(instance=instance, deleted=False)
    volume_data = VolumeSerializer(volume_set, many=True).data
    instance_data['volume_list'] = volume_data

    return Response(instance_data)

#update by dongdong
@api_view(["GET"])
def vdi_view(request):
    LOG.info("****** i am vdi view with method get ********")

    queryset = Instance.objects.all().filter(deleted=False, user_id=request.user.id)
    json_value = {}
    count = 0 
    method = "responseUserCheck"
    retvalue = "0"
    vminfo = []
    for q in queryset:
        LOG.info("******")
        novaAdmin = get_nova_admin(request)
        LOG.info("******")
        if not q.uuid:
            continue
        server = novaAdmin.servers.get(q.uuid)
        LOG.info("******")
        server_dict = server.to_dict()
        LOG.info("******")
        server_host = server_dict['OS-EXT-SRV-ATTR:host']
        server_status = server_dict['status']
        LOG.info("******* server_status is *******" + str(server_status))
        if server_status == "ERROR":
            continue
        host_ip = settings.COMPUTE_HOSTS[server_host]
        LOG.info("host ip is" + str(host_ip))
        cmd="virsh -c qemu+tcp://" + host_ip + "/system vncdisplay " + q.uuid
        LOG.info("cmd=" + cmd)
        p = subprocess.Popen("virsh -c qemu+tcp://" + host_ip + "/system vncdisplay " + q.uuid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        port = None
        for line in p.stdout.readlines():
            port = line
            break
        LOG.info("host_ip=" + host_ip)
        LOG.info("port=" + str(port))
        if "error" in str(port):
            vminfo.append({"vm_uuid": q.uuid, "vm_public_ip": q.public_ip, "vm_serverip": host_ip, "vm_status": server_status, "vnc_port": "no port", "vm_internalid": str(q.id), "vm_name": q.name})
            count = count + 1
            continue
        split_port = port.split(":")
        port_1 = split_port[1]
        port_2 = port_1.split("\\")
        port_3 = port_2[0]
        vnc_port = 5900 + int(port_3)
        vminfo.append({"vm_uuid": q.uuid, "vm_public_ip": q.public_ip, "vm_serverip": host_ip, "vm_status": server_status, "vnc_port": vnc_port, "vm_internalid": str(q.id), "vm_name": q.name})
        LOG.info("*** count is ***" + str(count))
        count = count + 1

    json_value = {"method": method, "retvalue": retvalue, "vmnum": count, "vminfo": vminfo}
    if not json_value:
        json_value = {"retval": 1, "message": "auth success"}
    
    return Response(json_value)

@api_view(["POST"])
def instance_action_view(request, pk):
    LOG.info("9999999999")
    instance_id, action = request.data['instance'], request.data['action']
    LOG.info("instance id is" + str(instance_id))
    LOG.info("action is" + str(action))
    data = instance_action(request.user, instance_id, action)
    return Response(data)

@api_view(["GET"])
def instance_action_vdi_view(request):
    LOG.info("9999999999")
    instance_id = request.GET.get('instance')
    action = request.GET.get('action')
    #instance_id, action = request.data['instance'], request.data['action']
    LOG.info("instance id is" + str(instance_id))
    LOG.info("action is" + str(action))
    data = instance_action(request.user, instance_id, action)
    return Response(data)


@require_GET
def monitor_settings(request):
    monitor_config = settings.MONITOR_CONFIG.copy()
    monitor_config['intervals'] = MonitorInterval.\
        filter_options(monitor_config['intervals'])

    monitor_config.pop('base_url')

    return Response(monitor_config)


class MonitorProxy(HttpProxy):
    base_url = settings.MONITOR_CONFIG['base_url']

    forbidden_pattern = re.compile(r"elasticsearch/.kibana/visualization/")

    def proxy(self):
        url = self.kwargs.get('url', '')

        if self.forbidden_pattern.search(url):
            return HttpResponse('', status=status.HTTP_403_FORBIDDEN)

        return super(MonitorProxy, self).proxy()

@csrf_exempt
@api_view(["GET"])
def new_vdi_test(request):

    LOG.info("start to get data")
    method = request.GET.get("method")
    retval = 0 
    if method == "requestCheckUser":
        LOG.info("** method is ***" + str(method))
        username = request.GET.get("username")
        password = request.GET.get("password")
        LOG.info("*** username is ***" + str(username))
        LOG.info("*** user password is ***" + str(password))
        user = authenticate(username=username, password=password)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                LOG.info("*** user is active")
                retval = 1
            else:
                retval = -1
                LOG.info("*** user is not active")
        else:
            retval = -2
            LOG.info("*** auth failed ***")

 
    response_value = {"status": retval}
    LOG.info("*** start to return ***")
    username = "klkl"
    password = "ydd1121NN"
    user = authenticate(username=username, password=password)
    login(request, user)

    LOG.info("*** user is ***" + str(request.user))
    if user.is_authenticated:
        LOG.info("user is authenticated")
    queryset = Instance.objects.all().filter(deleted=False, user_id=request.user.id)
    json_value = {}
    for q in queryset:
        LOG.info("******")
        novaAdmin = get_nova_admin(request)
        LOG.info("******")
        if not q.uuid:
            continue
        server = novaAdmin.servers.get(q.uuid)
        LOG.info("******")
        server_dict = server.to_dict()
        LOG.info("******")
        server_host = server_dict['OS-EXT-SRV-ATTR:host']
        server_status = server_dict['status']
        LOG.info("******* server_status is *******" + str(server_status))
        if server_status == "ERROR":
            continue
        host_ip = settings.COMPUTE_HOSTS[server_host]
        LOG.info("host ip is" + str(host_ip))
        cmd="virsh -c qemu+tcp://" + host_ip + "/system vncdisplay " + q.uuid
        LOG.info("cmd=" + cmd)
        p = subprocess.Popen("virsh -c qemu+tcp://" + host_ip + "/system vncdisplay " + q.uuid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        port = None
        for line in p.stdout.readlines():
            port = line
            break
        LOG.info("host_ip=" + host_ip)
        LOG.info("port=" + str(port))
        if "error" in str(port):
            json_value[str(q.id)] = {"vm_uuid": q.uuid, "vm_private_ip": q.private_ip, "vm_public_ip": q.public_ip, "vm_host": host_ip, "vm_status": server_status, "policy_device": str(q.policy), "vnc_port": "no port", "vm_internalid": str(q.id), "vm_name": q.name}

            continue
        split_port = port.split(":")
        port_1 = split_port[1]
        port_2 = port_1.split("\\")
        port_3 = port_2[0]
        vnc_port = 5900 + int(port_3)
        json_value[str(q.id)] = {"vm_uuid": q.uuid, "vm_private_ip": q.private_ip, "vm_public_ip": q.public_ip, "vm_host": host_ip, "vm_status": server_status, "policy_device": str(q.policy), "vnc_port": vnc_port, "vm_internalid": str(q.id), "vm_name": q.name}
    LOG.info("*** json_value ***" + str(json_value))
    #return json_util.loads(json_value)
    return json_util.loads(json_value)

def user_is_not_active(request):
    return Response({"status": "-1", "message": "failed"})

def user_auth_failed(request):
    return Response({"status": "-1", "message": "failed"})

def new_vdi(request):
    LOG.info("start to get data")
    method = request.GET.get("method")
    retval = 0
    if method == "requestCheckUser":
        LOG.info("** method is ***" + str(method))
        username = request.GET.get("username")
        password = request.GET.get("password")
        LOG.info("*** username is ***" + str(username))
        LOG.info("*** user password is ***" + str(password))
        user = authenticate(username=username, password=password)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                LOG.info("*** user is active")
                retval = 1
            else:
                retval = -1
                LOG.info("*** user is not active")
        else:
            retval = -2
            LOG.info("*** auth failed ***")
    if retval == 1:
        json_value = vdi_view(request)
    if retval == -1:
        json_value = user_is_not_active(request)
    if retval == -2:
        json_value = user_auth_failed(request)
    return json_value

monitor_proxy = login_required(csrf_exempt(MonitorProxy.as_view()))
