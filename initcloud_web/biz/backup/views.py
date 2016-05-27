#coding=utf-8

import logging

from django.utils.translation import ugettext_lazy as _

from rest_framework.response import Response
from rest_framework import generics

from biz.account.models import Operation
from biz.instance.models import Instance
from biz.volume.models import Volume
from biz.idc.models import UserDataCenter
from biz.backup.models import BackupItem
from biz.backup.serializer import BackupItemSerializer, ChainSerializer
from biz.backup.settings import (BACKUP_STATE_PENDING_RESTORE,
                                 BACKUP_STATE_ERROR, BACKUP_STATE_DELETED,
                                 BACKUP_STATE_PENDING_DELETE)
from cloud import tasks

from biz.common.pagination import PagePagination
from biz.common.decorators import require_POST, require_GET
from biz.common.utils import fail, success, error, retrieve_params

LOG = logging.getLogger(__name__)


@require_POST
def backup_instance(request):

    instance_id, name, is_full = retrieve_params(
        request.data, 'instance_id', 'name', 'is_full')

    udc = UserDataCenter.objects.get(pk=request.session["UDC_ID"])
    volume_ids = request.data.getlist('volume_ids[]')
    is_full = True if is_full == 'true' else False

    instance = Instance.objects.get(pk=instance_id)
    volumes = Volume.objects.filter(pk__in=volume_ids)

    if BackupItem.is_any_unstable(resource=instance):
        return fail(_("Instance %(name)s has one backup task now.")
                    % {'name': instance.name})

    if BackupItem.has_error_node_on_default_chain(resource=instance):
        return fail(_("Instance %(name)s has one error backup node on "
                      "default backup chain. Please delete it first")
                    % {'name': instance.name})

    for volume in volumes:
        if BackupItem.is_any_unstable(resource=volume):
            return fail(_("Volume %(name)s has one backup task now.")
                        % {'name': volume.name})

        if BackupItem.has_error_node_on_default_chain(resource=volume):
            return fail(_("Volume %(name)s has one error backup node on "
                        "default backup chain. Please delet it first")
                        % {'name': volume.name})

    items = [BackupItem.create(instance, name, request.user,
                               udc, is_full=is_full)]

    Operation.log(instance, obj_name=instance.name, action="backup")

    for volume in volumes:
        items.append(BackupItem.create(volume, name, request.user, udc,
                                       is_full=is_full))
        Operation.log(volume, obj_name=volume.name, action="backup")

    for item in items:
        tasks.execute_backup.delay(item.id)

    return success(_("Backup is in process."))


@require_POST
def backup_volume(request):

    volume_id, name, is_full = retrieve_params(
        request.data, 'volume_id', 'name', 'is_full')

    udc = UserDataCenter.objects.get(pk=request.session["UDC_ID"])
    is_full = True if is_full == 'true' else False

    volume = Volume.objects.get(pk=volume_id)

    if BackupItem.is_any_unstable(resource=volume):
        return fail(_("Volume %(name)s has one backup task now.")
                    % {'name': volume.name})

    if BackupItem.has_error_node_on_default_chain(resource=volume):
        return fail(_("Volume %(name)s has one error backup node on "
                    "default backup chain. Please delete it first")
                    % {'name': volume.name})

    item = BackupItem.create(volume, name, request.user, udc, is_full=is_full)

    Operation.log(volume, obj_name=volume.name, action="backup")
    tasks.execute_backup.delay(item.id)

    return success(_("Backup is in process."))


class BackupChainList(generics.ListAPIView):

    serializer_class = ChainSerializer
    queryset = BackupItem.living.all()
    pagination_class = PagePagination

    def get_queryset(self):
        request = self.request
        udc_id = request.session["UDC_ID"]
        queryset = super(BackupChainList, self).get_queryset()

        queryset = queryset.filter(is_full=True,
                                   user=request.user,
                                   user_data_center__id=udc_id)

        return queryset.order_by('-id')


@require_GET
def get_chain(request, chain_id):
    items = BackupItem.living.filter(chain_id=chain_id).order_by('-id')
    serializer = BackupItemSerializer(items, many=True)

    return Response(serializer.data)


@require_POST
def restore_backup_item(request, pk):

    backup_item = BackupItem.objects.get(pk=pk)

    if BackupItem.is_any_unstable(resource_id=backup_item.resource_id,
                                  resource_type=backup_item.resource_type):

        return fail(_("Resource %(name)s has one backup task now.")
                    % {'name': backup_item.resource.name})

    if backup_item.status == BACKUP_STATE_ERROR:
        return fail(_("This backup item is available."))

    if backup_item.is_instance_backup:
        instance = Instance.objects.get(pk=backup_item.resource_id)

        if instance.deleted:
            return fail(_("Cannot restore, because target resource has "
                          "already been deleted"))

        if instance.is_running:
            return fail(_("Cannot restore, because target instance is running"))

    else:
        volume = Volume.objects.get(pk=backup_item.resource_id)
        if volume.deleted:
            return fail(_("Cannot restore, because target resource has "
                          "already been deleted"))

        if volume.instance and volume.instance.is_running:
            return fail(_("Cannot restore, because target volume is attached to"
                          " a running instance, stop the instance or "
                          "detach the volume"))

    Operation.log(backup_item, obj_name=backup_item.name, action="restore")

    backup_item.change_status(BACKUP_STATE_PENDING_RESTORE)

    if tasks.restore_snap(backup_item.id):
        return success(_("Restoring"))
    else:
        LOG.error("Failed to restore backup item. %s", backup_item)
        return error()


@require_POST
def delete_backup_item(request, pk):

    backup_item = BackupItem.objects.get(pk=pk)

    if backup_item.status == BACKUP_STATE_ERROR or \
            backup_item.rbd_image is None:
        backup_item.deleted = True
        backup_item.change_status(BACKUP_STATE_DELETED)
        backup_item.save()
        return success(_("Backup item Deleted."))

    if BackupItem.is_any_node_untable(backup_item.chain_id):
        return fail(_("There is one task running on this chain."))

    BackupItem.mark_chain_delete(backup_item)

    Operation.log(backup_item, obj_name=backup_item.name, action="delete")

    try:
        tasks.delete_backup.delay(backup_item.id)
    except Exception:
        LOG.exception("Failed to delete backup item. %s", backup_item)
        return error()
    else:
        return success(_("Deleting"))
