import logging

from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.response import Response

from biz.instance.models import Instance
from biz.account.models import Operation
from biz.idc.models import UserDataCenter

from .models import (BalancerPool, BalancerMember, BalancerVIP,
                     BalancerMonitor, BalancerPoolMonitor)
from .serializer import (BalancerPoolSerializer, BalancerMemberSerializer,
                         BalancerVIPSerializer, BalancerMonitorSerializer)
from .settings import (POOL_DELETING, POOL_UPDATING, POOL_ACTIVE, PROTOCOL_CHOICES,
                       LB_METHOD_CHOICES, MONITOR_TYPE, POOL_STATES_DICT,
                       SESSION_PER_CHOICES, POOL_ERROR)

from cloud.loadbalancer_task import (pool_create_task, pool_update_task,
                                     pool_delete_task, pool_vip_create_task,
                                     pool_vip_update_task, pool_vip_delete_task,
                                     pool_member_create_task,
                                     pool_member_update,
                                     pool_member_delete_task,
                                     pool_monitor_create, pool_monitor_update,
                                     pool_monitor_delete,
                                     pool_monitor_association_create,
                                     pool_monitor_association_delete)

from biz.common.decorators import require_GET, require_POST
from biz.common.utils import fail, error, success

LOG = logging.getLogger(__name__)


@require_GET
def pool_list_view(request):
    query_set = BalancerPool.living.filter(
        user=request.user, user_data_center=request.session["UDC_ID"])
    return Response(BalancerPoolSerializer(query_set, many=True).data)


@require_GET
def pool_get_view(request, pk):
    try:
        pool = BalancerPool.objects.get(pk=pk, user=request.user)
        return Response(BalancerPoolSerializer(pool).data)
    except BalancerPool.DoesNotExist:
        return Response({"OPERATION_STATUS": 0, "MSG": _('Balancer no exists')})


@api_view(['POST'])
def create_pool(request):

    serializer = BalancerPoolSerializer(data=request.data,
                                        context={"request": request})
    if not serializer.is_valid():
        return fail(_('Data is not valid'))

    pool = serializer.save()
    Operation.log(pool, obj_name=pool.name, action='create', result=1)

    try:
        pool_create_task.delay(pool)
        return success(_('Creating balancer pool.'))
    except Exception:
        LOG.exception("Failed to create balancer pool")
        pool.status = POOL_ERROR
        pool.save()
        return error()


@require_POST
def update_pool(request):
    pool_id = request.data['id']

    pool = BalancerPool.objects.get(
        pk=pool_id, user=request.user,
        user_data_center=request.session["UDC_ID"])

    serializer = BalancerPoolSerializer(data=request.data,
                                        instance=pool,
                                        context={"request": request})

    if not serializer.is_valid():
        return fail(_('Data is not valid'))

    pool.status = POOL_UPDATING
    pool = serializer.save()

    Operation.log(pool, obj_name=pool.name, action='update')
    try:
        pool_update_task.delay(pool)
        return success(_('Updating balancer pool.'))
    except Exception:
        LOG.exception("Failed to update balancer pool.")
        return error()


@api_view(['POST'])
def delete_pool(request):

    pool_id = request.data['pool_id']

    try:
        pool = BalancerPool.objects.get(
            pk=pool_id, user=request.user,
            user_data_center=request.session["UDC_ID"])
    except BalancerPool.DoesNotExist:
        return fail(_('No balancer found.'))

    if not pool.pool_uuid:
        pool.deleted = True
        pool.save()
        return success(_('Balancer pool %(name)s is deleted')
                       % {'name': pool.name})

    pool.status = POOL_DELETING
    pool.save()
    Operation.log(pool, obj_name=pool.name, action='delete')

    try:
        pool_delete_task.delay(pool)
    except Exception:
        LOG.exception("Failed to delete balancer pool[%s]", pool)
        return error()

    return success(_('Deleting balancer pool %(name)s') % {'name': pool.name})


@require_POST
def create_pool_vip(request):

    pool_id = request.data['pool_id']
    try:
        pool = BalancerPool.objects.get(
            pk=pool_id, user=request.user,
            user_data_center=request.session["UDC_ID"])
    except BalancerPool.DoesNotExist:
        return fail(_("No balancer pool found!"))

    serializer = BalancerVIPSerializer(data=request.data,
                                       context={'request': request})

    if not serializer.is_valid():
        return fail(_('Data is not valid'))

    vip = serializer.save()
    Operation.log(vip, obj_name=vip.name, action='create')

    pool.status = POOL_UPDATING
    pool.save()

    try:
        pool_vip_create_task.delay(vip, pool)
    except Exception:
        vip.delete()
        return error()

    return success(_('Creating balancer vip.'))


@require_POST
def update_pool_vip(request):

    vip_id = request.data['id']
    try:
        vip = BalancerVIP.objects.get(pk=vip_id, user=request.user)
    except BalancerVIP.DoesNotExist:
        return fail(_("No VIP found."))

    vip.session_persistence = int(request.data['session_persistence'])
    vip.name = request.data['name']
    vip.description = request.data['description']

    Operation.log(vip, obj_name=vip.name, action='update', result=1)

    if pool_vip_update_task(vip):
        vip.save()
        return success(_('Vip update success'))
    else:
        return fail(_('Vip update fail'))


@api_view(['POST'])
def pool_vip_delete_view(request):
    pool_id = request.data['id']

    pool = BalancerPool.objects.get(pk=pool_id, user=request.user)
    vip = BalancerVIP.objects.get(pk=pool.vip.id, user=request.user,
                                  user_data_center=request.session["UDC_ID"])

    try:
        pool_vip_delete_task.delay(vip, pool)
    except Exception:
        return error()
    else:
        Operation.log(vip, obj_name=vip.name, action='delete', result=1)
        return success(_('Deleting balancer vip '))


@api_view(['POST'])
def execute_pool_monitor_action(request):
    pool_id = request.data["pool_id"]
    monitor_id = request.data["monitor_id"]
    action = request.data["action"]

    pool = BalancerPool.objects.get(pk=pool_id, user=request.user)
    monitor = BalancerMonitor.objects.get(pk=monitor_id, user=request.user)

    if action == 'attach':
        return attach_monitor_to_pool(pool, monitor)
    else:
        return detach_monitor_from_pool(pool, monitor)


def attach_monitor_to_pool(pool, monitor):

    Operation.log(pool, obj_name=pool.name, action='attach')

    if pool_monitor_association_create(pool, monitor):
        return success(_('Monitor is attached.'))
    else:
        return error()


def detach_monitor_from_pool(pool, monitor):

    Operation.log(pool, obj_name=pool.name, action='detach', result=1)

    if pool_monitor_association_delete(pool, monitor):
        return success(_('Monitor is detached'))
    else:
        return error()


@api_view(['GET', 'POST'])
def pool_member_list_view(request, balancer_id=None):
    query_set = BalancerMember.objects.filter(
        deleted=False, pool=balancer_id,  user=request.user,
        user_data_center=request.session["UDC_ID"])
    serializer = BalancerMemberSerializer(query_set, many=True)
    return Response(serializer.data)


@require_POST
def create_pool_member(request):

    serializer = BalancerMemberSerializer(data=request.data,
                                          context={'request': request})

    if not serializer.is_valid():
        return fail(_('Data is not valid.'))

    pool_id = request.data['pool_id']
    user = request.user
    udc = UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    try:
        pool = BalancerPool.objects.get(pk=pool_id, user=request.user)
    except BalancerPool.DoesNotExist:
        return fail(_('Selected balancer not found.'))

    weight = int(request.data['weight'])
    protocol_port = int(request.data['protocol_port'])

    for instance_id in request.data.getlist('instance_ids[]'):

        instance = Instance.objects.get(pk=instance_id, user=request.user)

        member = BalancerMember.objects.create(
            pool=pool, weight=weight, protocol_port=protocol_port,
            user=user, user_data_center=udc, instance=instance
        )
        Operation.log(member, obj_name=instance.name, action='create')
        pool_member_create_task.delay(member)

    return success(_("Load balancer members are being created."))


@require_POST
def update_pool_member(request):
    member_id = request.data['id']

    try:
        member = BalancerMember.objects.get(pk=member_id, user=request.user)
    except BalancerMember.DoesNotExist:
        return fail(_("Member not found."))

    member.weight = int(request.data['weight'])

    if pool_member_update(member):
        Operation.log(member, obj_name=member.instance.name, action='update')
        member.save()
        return success(_("Member is updated!"))
    else:
        return error()


@require_POST
def delete_pool_member(request):
    member_id = request.data['id']
    try:
        member = BalancerMember.objects.get(pk=member_id)
    except BalancerMember.DoesNotExist:
        return success(_("Member is deleted."))

    if not member.member_uuid:
        member.deleted = True
        member.save()
        Operation.log(member, obj_name=member.instance.name, action='delete')
        return success(_("Member is deleted."))

    member.status = POOL_DELETING
    member.save()

    try:
        pool_member_delete_task.delay(member)
    except Exception:
        member.status = POOL_ACTIVE
        return error()
    else:
        return success(_("Deleting member"))


@api_view(['GET', 'POST'])
def pool_monitor_list_view(request):
    query_set = BalancerMonitor.objects.filter(
        deleted=False, user=request.user,
        user_data_center=request.session["UDC_ID"])
    serializer = BalancerMonitorSerializer(query_set, many=True)
    return Response(serializer.data)


@require_POST
def create_pool_monitor(request):
    serializer = BalancerMonitorSerializer(data=request.data,
                                           context={'request': request})

    if not serializer.is_valid():
        return fail(_("Monitor Data is not valid"))

    monitor = serializer.save()
    Operation.log(monitor, obj_name=monitor.get_type_display(),
                  action='create')

    if pool_monitor_create(monitor):
        return success(_("Balancer monitor is created."))
    else:
        monitor.delete()
        return error()


@require_POST
def update_pool_monitor(request):

    monitor_id = request.data['id']

    try:
        monitor = BalancerMonitor.objects.get(pk=monitor_id, user=request.user)
    except BalancerMonitor.DoesNotExist:
        return fail(_("No monitor found!"))

    serializer = BalancerMonitorSerializer(data=request.data,
                                           instance=monitor,
                                           context={'request': request})

    if not serializer.is_valid():
        return fail(_("Monitor data is not valid"))

    monitor.delay = int(request.data['delay'])
    monitor.timeout = int(request.data['timeout'])
    monitor.max_retries = int(request.data['max_retries'])

    if pool_monitor_update(monitor):
        monitor.save()
        Operation.log(monitor, obj_name=monitor.get_type_display(),
                      action='update')
        return success(_('Balancer monitor is updated!'))
    else:
        return error()


@require_POST
def delete_pool_monitor(request):

    monitor_id = request.data['id']

    monitor = BalancerMonitor.objects.get(pk=monitor_id, user=request.user)

    if BalancerPoolMonitor.objects.filter(monitor=monitor).exists():
        return fail(_("Monitor %(name)s is being used, can not be deleted.")
                    % {'name': monitor.name})

    if pool_monitor_delete(monitor):
        Operation.log(monitor, obj_name=monitor.get_type_display(), action='delete')
        return success(_('Balancer monitor is deleted.'))
    else:
        return error()


@api_view(['GET'])
def get_constant_view(request):
    return Response({'protocol': PROTOCOL_CHOICES,
                     'lb_method': LB_METHOD_CHOICES,
                     "monitor_type": MONITOR_TYPE,
                     "session_per": SESSION_PER_CHOICES})


@api_view(['GET'])
def get_status_view(request):
    return Response(POOL_STATES_DICT)


@require_GET
def get_available_monitor_view(request):
    pool_id = request.query_params['pool_id']
    action = request.query_params['action']

    monitors = BalancerMonitor.objects.filter(deleted=False, user=request.user)
    if action == 'attach':
        monitors = monitors.exclude(monitor_re__pool=pool_id)
    elif action == 'detach':
        monitors = monitors.filter(monitor_re__pool=pool_id)

    serializer = BalancerMonitorSerializer(monitors, many=True)
    return Response(serializer.data)
