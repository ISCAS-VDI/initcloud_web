import logging

from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response
from rest_framework.decorators import api_view

from biz.common.decorators import require_POST, require_GET
from biz.common.utils import fail, error, success
from biz.instance.models import Instance
from biz.account.models import Operation
from biz.firewall.models import Firewall
from biz.firewall.settings import SECURITY_GROUP_RULES
from biz.firewall.serializer import *
from cloud.network_task import (security_group_create_task,
                                security_group_delete_task,
                                security_group_rule_delete_task,
                                security_group_rule_create_task,
                                server_update_security_groups_task)

LOG = logging.getLogger(__name__)


@require_GET
def firewall_list_view(request):
    firewall_set = Firewall.objects.filter(
        deleted=False, user=request.user,
        user_data_center=request.session["UDC_ID"])
    serializer = FirewallSerializer(firewall_set, many=True)
    return Response(serializer.data)


@require_POST
def firewall_create_view(request):
    serializer = FirewallSerializer(data=request.data,
                                    context={"request": request})
    if not serializer.is_valid():
        return fail(_('Data is not valid.'))

    firewall = serializer.save()
    Operation.log(firewall, obj_name=firewall.name, action="create")

    try:
        security_group_create_task.delay(firewall)
    except Exception:
        LOG.exception("Failed to create firewall")
        firewall.delete()
        return error()

    return success(_('Creating firewall'))


@require_POST
def firewall_delete_view(request):
    data = request.data
    firewall = Firewall.objects.get(pk=data.get('id'))

    if firewall.is_default:
        return fail(_("Firewall %(name)s is the default firewall, "
                      "cannot be deleted.") % {'name': firewall.name})

    if firewall.is_in_use:
        msg = _('Firewall %(name)s is being used.') % {'name': firewall.name}
        return fail(msg)

    Operation.log(firewall, obj_name=firewall.name, action="terminate")
    if firewall.firewall_id:
        try:
            security_group_delete_task(firewall)
        except Exception:
            LOG.exception("Failed to delete firewall. %s", firewall)
            return error()

    firewall.deleted = True
    firewall.save()
    return success(_("Firewall %(name)s is deleted") % {'name': firewall.name})


@require_GET
def firewall_rule_list_view(request, firewall_id):
    rule_set = FirewallRules.objects.filter(
        deleted=False, user=request.user, firewall=firewall_id,
        user_data_center=request.session["UDC_ID"])

    serializer = FirewallRulesSerializer(rule_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def firewall_rule_create_view(request):
    data = request.data
    firewall_id = data.get('firewall')
    if not firewall_id:
        return Response({'OPERATION_STATUS': 0,
                         'MSG': _('no selected security group')})

    serializer = FirewallRulesSerializer(data=request.data,
                                         context={'request': request})

    if not serializer.is_valid():
        return Response({'OPERATION_STATUS': 0,
                         'MSG': _('Valid firewall rule nopass')})

    firewall_rule = serializer.save()

    obj_name = firewall_rule.protocol if firewall_rule.protocol else ""
    Operation.log(firewall_rule, obj_name=obj_name.upper(), action="create")

    try:
        security_group_rule_create_task.delay(firewall_rule)
    except Exception:
        firewall_rule.delete()
        return Response({'OPERATION_STATUS': 0,
                         'MSG': _('Create firewall rule error')})

    return Response({'OPERATION_STATUS': 1,
                     'MSG': _('Create firewall rule success')})


@api_view(['POST'])
def firewall_rule_delete_view(request):
    data = request.data

    try:
        firewall_rule = FirewallRules.objects.get(pk=data.get('id'))
    except FirewallRules.DoesNotExist:
        return fail(_("Firewall rule not exists."))

    obj_name = firewall_rule.protocol if firewall_rule.protocol else ""
    Operation.log(firewall_rule, obj_name=obj_name.upper(), action="terminate")

    if security_group_rule_delete_task(firewall_rule):
        return success(_("Firewall Rule is deleted."))
    else:
        return error()


@api_view(['GET'])
def firewall_rule_view(request):
    return Response(SECURITY_GROUP_RULES)


@api_view(['POST'])
def instance_change_firewall_view(request):
    data = request.data

    try:
        instance = Instance.objects.get(pk=data['instance_id'])
    except Instance.DoesNotExist:
        return fail(_("Instance is not found"))

    try:
        firewall = Firewall.objects.get(pk=data.get('firewall_id'))
    except Firewall.DoesNotExist:
        return fail(_("Firewall is not found"))

    Operation.log(instance, obj_name=instance.name, action="change_firewall")

    try:
        server_update_security_groups_task.delay(instance, firewall)
    except Exception:
        LOG.exception("Failed to change firewall group of instance. %s",
                      instance)
        return error()

    return success(_("Instance %(name)s's firewall is changed.")
                   % {'name': instance.name})
