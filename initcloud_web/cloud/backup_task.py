#-*- coding=utf-8 -*-

from __future__ import absolute_import

import datetime
import logging

from django.conf import settings
from cloud.celery import app
from celery.exceptions import SoftTimeLimitExceeded

from fabric import tasks
from fabric.api import run, env
from fabric.network import disconnect_all
from fabric.exceptions import NetworkError

from biz.backup.settings import (BACKUP_STATE_BACKUPING, BACKUP_STATE_AVAILABLE,
                                 BACKUP_STATE_ERROR, BACKUP_STATE_DELETING,
                                 BACKUP_STATE_PENDING_RESTORE,
                                 BACKUP_STATE_DELETED, BACKUP_STATE_WAITING,
                                 BACKUP_STATE_PENDING_DELETE,
                                 BACKUP_STATE_RESTORING)
from biz.backup.models import BackupItem, BackupLog

LOG = logging.getLogger("cloud.tasks")

env.hosts = [
    settings.BACKUP_RBD_HOST,
]

env.passwords = {
    settings.BACKUP_RBD_HOST: settings.BACKUP_RBD_HOST_PWD,
}

env.warn_only = True
env.skip_bad_hosts = True


def utcnow():
    return datetime.datetime.utcnow()


def next_query_time():
    return utcnow() + settings.BACKUP_QUERY_INTERVAL


def query_expire_date():
    return utcnow() + settings.BACKUP_QUERY_MAX_DURATION


def time_since(start):
    return (datetime.datetime.now() - start).seconds


def run_cmd(cmd):

    try:
        results = tasks.execute(lambda: run(cmd))
        return results[settings.BACKUP_RBD_HOST]
    finally:
        disconnect_all()


def _format_pool(backup_item):
    if backup_item.is_instance_backup:
        return ("%s_disk" % backup_item.resource_uuid,
                settings.RBD_COMPUTE_POOL)

    if backup_item.is_volume_backup:
        return ("volume-%s" % backup_item.resource_uuid,
                settings.RBD_VOLUME_POOL)

    raise Exception("Unsupported resource_type (%s)"
                    % backup_item.resource_type)


def generate_command(backup_item, command_template, **kwargs):

    args = settings.BACKUP_COMMAND_ARGS.copy()
    args["image"], args["source_pool"] = _format_pool(backup_item)
    args.update(kwargs)
    return command_template % args


@app.task(soft_time_limit=settings.BACKUP_CONNECTION_TIMEOUT)
def execute_backup(backup_item_id):

    try:
        backup_item = BackupItem.objects.get(pk=backup_item_id)
    except BackupItem.DoesNotExist:
        LOG.error("Backup Item of ID: %s doesn't exist", backup_item_id)
        return False

    LOG.info("BackupItem [backup] start. %s.", backup_item)

    if backup_item.status != BACKUP_STATE_WAITING:
        LOG.info("BackupItem [backup] end, status error: [%s][=%s].",
                 backup_item.status, BACKUP_STATE_WAITING)
        return False

    mode = 'incr' if backup_item.parent else 'full'
    cmd = generate_command(backup_item, settings.BACKUP_COMMAND, mode=mode)

    result, start = None, datetime.datetime.now()
    try:
        result = run_cmd(cmd)
    # Don't delete SoftTimeLimitExceed.
    except (SoftTimeLimitExceeded, Exception):
        LOG.exception("BackupItem backup exception, apply [%s] seconds. %s.",
                      time_since(start), backup_item)
        backup_item.change_status(BACKUP_STATE_ERROR)
        return False

    if isinstance(result, NetworkError):
        backup_item.status = BACKUP_STATE_ERROR
        backup_item.save()
        LOG.critical("Fabric Error. Cannot connect to host")
        return

    duration = time_since(start)

    if result.return_code == 0:
        backup_item.status = BACKUP_STATE_BACKUPING
        backup_item.rbd_image = result
        backup_item.save()
        LOG.info("uuid: %s", result)

        log = BackupLog.log_backup(backup_item)
        backup_progress_query.apply_async(args=(backup_item.id, log.id,
                                                query_expire_date()),
                                          eta=next_query_time())
        LOG.info("BackupItem [backup] end,  apply [%s] seconds. %s.",
                 duration, backup_item)
    else:
        backup_item.status = BACKUP_STATE_ERROR
        backup_item.save()

        LOG.info("BackupItem [backup] error,  apply [%s] seconds. %s.",
                 duration, backup_item)

    return result.return_code == 0


@app.task(soft_time_limit=settings.BACKUP_CONNECTION_TIMEOUT)
def backup_progress_query(backup_item_id, log_id, expire_date):
    """ Query backup progress for one backup task

    :param backup_item_id:  backup item id
    :param log_id:  backup log id
    :param expire_date:  when to stop query even backup task is not complete.
    :return: query result. True or False
    """

    backup_item = BackupItem.objects.get(pk=backup_item_id)

    if utcnow() > expire_date:
        backup_item.change_status(BACKUP_STATE_ERROR)
        LOG.error("Backup expired. %s", backup_item)
        return

    LOG.info("Begin to query backup item progress. %s", backup_item)

    cmd = generate_command(backup_item,
                           settings.BACKUP_QUERY_COMMAND,
                           rbd_image=backup_item.rbd_image)

    start = datetime.datetime.now()
    try:
        result = run_cmd(cmd)
    # Don't delete SoftTimeLimitExceeded
    except (SoftTimeLimitExceeded, Exception):
        LOG.exception("Backup progress query error, apply [%s] seconds. %s.",
                      time_since(start), backup_item)
        backup_progress_query.apply_async(args=(backup_item_id, log_id,
                                                expire_date),
                                          eta=next_query_time())
        return False

    duration = time_since(start)
    is_network_error = isinstance(result, NetworkError)

    # Need one result code to mark the backup job has exited accidentally
    if is_network_error or result.return_code != 0:

        if is_network_error:
            backup_progress_query.apply_async(args=(backup_item_id, log_id,
                                                    expire_date),
                                              eta=next_query_time())
            LOG.critical("Fabric Error. Cannot connect to host")
        else:
            backup_item.change_status(BACKUP_STATE_ERROR)
            BackupLog.end_backup(log_id, is_success=False)
            LOG.error("Backup failed, apply [%s] seconds. %s",
                      duration, backup_item)

        return False

    progress = int(result)

    if progress >= 100:
        backup_item.change_status(BACKUP_STATE_AVAILABLE)
        LOG.info("Backup is complete, apply [%s] seconds. %s.",
                 duration, backup_item)

        BackupLog.end_backup(log_id, is_success=True)
        du_snap(backup_item.id, log_id)
        return True
    elif progress < 0:
        backup_item.change_status(BACKUP_STATE_ERROR)
        LOG.error("Backup failed, apply [%s] seconds. %s",
                  duration, backup_item)
        BackupLog.end_backup(log_id, is_success=False)
        return False
    else:
        backup_item.progress = progress
        backup_item.save()
        BackupLog.objects.filter(pk=log_id).update(progress=progress)
        backup_progress_query.apply_async(args=(backup_item_id, log_id,
                                                expire_date),
                                          eta=next_query_time())

        LOG.info("Progress of backup item is %d, apply [%s] seconds. %s",
                 progress, duration, backup_item)
        return True


@app.task(soft_time_limit=settings.BACKUP_CONNECTION_TIMEOUT)
def du_snap(backup_item_id, log_id):

    backup_item = BackupItem.objects.get(pk=backup_item_id)

    LOG.info("Begin to query backup disk usage. %s", backup_item)

    cmd = generate_command(backup_item,
                           settings.BACKUP_DU_COMMAND,
                           rbd_image=backup_item.rbd_image)

    start = datetime.datetime.now()
    try:
        result = run_cmd(cmd)
    # Don't delete SoftTimeLimitExceed.
    except (SoftTimeLimitExceeded, Exception):
        LOG.exception("Failed to query backup disk usage, "
                      "apply [%s] seconds. %s", time_since(start), backup_item)
        return False

    duration = time_since(start)

    if isinstance(result, NetworkError):
        LOG.critical("Fabric Error. Cannot connect to host")
        return False

    if result.return_code == 0:
        backup_item.disk_usage = int(result)
        backup_item.save()
        LOG.info("Query backup disk usage end, disk usage: %s MB, "
                 "apply [%s] seconds. %s.",
                 backup_item.disk_usage, duration, backup_item)
        BackupLog.objects.filter(pk=log_id).update(
            disk_usage=backup_item.disk_usage)
        return True
    else:
        LOG.exception("Cannot query disk usage for backup item, "
                      "apply [%] seconds. %s", duration, backup_item)
        return False


@app.task(soft_time_limit=settings.BACKUP_CONNECTION_TIMEOUT)
def restore_snap(backup_item_id):

    backup_item = BackupItem.objects.get(pk=backup_item_id)

    if backup_item.status != BACKUP_STATE_PENDING_RESTORE:
        LOG.error("BackupItem [restore] end, status error: [%s][=%s].",
                  backup_item.status, BACKUP_STATE_PENDING_RESTORE)
        return False

    if not backup_item.rbd_image:
        LOG.error("BackupItem [restore] end, rbd_image is None.")
        return False

    LOG.info("BackupItem [restore] start, [%s].", backup_item)
    begin = datetime.datetime.now()
    cmd = generate_command(backup_item,
                           settings.BACKUP_RESTORE_COMMAND,
                           rbd_image=backup_item.rbd_image)

    try:
        result = run_cmd(cmd)
    # Don't delete SoftTimeLimitExceed.
    except (SoftTimeLimitExceeded, Exception):
        LOG.exception("BackupItem restore exception, apply [%s] seconds",
                      time_since(begin), backup_item)
        backup_item.change_status(BACKUP_STATE_AVAILABLE)
        return False

    duration = time_since(begin)
    is_network_error = isinstance(result, NetworkError)

    if is_network_error or result.return_code != 0:
        backup_item.change_status(BACKUP_STATE_AVAILABLE)
        if is_network_error:
            LOG.critical("Fabric Error. Cannot connect to host")
        else:
            LOG.info("BackupItem restore error, apply [%s] seconds. [%s]",
                     duration, backup_item)
        return False

    backup_item.progress = 0
    backup_item.change_status(BACKUP_STATE_RESTORING)
    log = BackupLog.log_restore(backup_item)
    restore_progress_query.apply_async(args=(backup_item.id, log.id,
                                             query_expire_date()),
                                       eta=next_query_time())

    LOG.info("BackupItem restore end, apply [%s] seconds. [%s]",
             duration, backup_item)

    return True


@app.task(soft_time_limit=settings.BACKUP_CONNECTION_TIMEOUT)
def restore_progress_query(backup_item_id, log_id, expire_date):
    """ Query restore progress for one restore task

    :param backup_item_id:  backup item id
    :param log_id:  backup log id
    :param expire_date:  when to stop query even restore task is not complete.
    :return: query result. True or False
    """

    backup_item = BackupItem.objects.get(pk=backup_item_id)

    if utcnow() > expire_date:
        backup_item.change_status(BACKUP_STATE_ERROR)
        LOG.error("Backup restore expired. %s", backup_item)
        return False

    LOG.info("Begin to query backup item restore progress. %s", backup_item)

    cmd = generate_command(backup_item,
                           settings.BACKUP_RESTORE_QUERY_COMMAND,
                           rbd_image=backup_item.rbd_image)

    start = datetime.datetime.now()
    try:
        result = run_cmd(cmd)
    # Don't delete SoftTimeLimitExceed.
    except (SoftTimeLimitExceeded, Exception):
        LOG.exception("Backup item restore process query error, "
                      "apply [%s] seconds. %s.", time_since(start), backup_item)
        restore_progress_query.apply_async(args=(backup_item_id, log_id,
                                                 expire_date),
                                           eta=next_query_time())
        return False

    duration = time_since(start)
    is_network_error = isinstance(result, NetworkError)

    if is_network_error or result.return_code != 0:

        if is_network_error:
            restore_progress_query.apply_async(args=(backup_item_id, log_id,
                                                     expire_date),
                                               eta=next_query_time())
            LOG.critical("Fabric Error. Cannot connect to host:%s", env.host)
        else:
            backup_item.change_status(BACKUP_STATE_AVAILABLE)
            LOG.error("Backup item restore error, apply [%s] seconds. %s",
                      duration, backup_item)
            BackupLog.end_restore(log_id, is_success=False)
        return False

    progress = int(result)

    if progress >= 100:
        backup_item.change_status(BACKUP_STATE_AVAILABLE)
        BackupItem.revoke_default_chain(backup_item.chain_id)
        LOG.info("Backup item restore complete, apply [%s] seconds. %s",
                 duration, backup_item)
        BackupLog.end_restore(log_id, is_success=True)
    elif progress < 0:
        backup_item.change_status(BACKUP_STATE_AVAILABLE)
        LOG.error("Backup item restore error, apply [%s] seconds. %s",
                  duration, backup_item)
        BackupLog.end_restore(log_id, is_success=False)
    else:
        backup_item.progress = progress
        backup_item.save()
        BackupLog.objects.filter(pk=log_id).update(progress=progress)
        restore_progress_query.apply_async(args=(backup_item_id, log_id,
                                                 expire_date),
                                           eta=next_query_time())

        LOG.info("Backup item restore progress: %d, apply [%s] seconds. %s",
                 progress, duration, backup_item)

    return progress >= 0


@app.task(soft_time_limit=settings.BACKUP_CONNECTION_TIMEOUT)
def delete_backup(backup_item_id):

    backup_item = BackupItem.objects.get(pk=backup_item_id)

    LOG.info("BackupItem [delete] start, [%s].", backup_item)

    if backup_item.status != BACKUP_STATE_PENDING_DELETE:
        LOG.info("BackupItem [delete] end, status error: [%s][=%s]",
                 backup_item.status, BACKUP_STATE_PENDING_DELETE)
        return False

    if not backup_item.rbd_image:
        LOG.info("BackupItem [delete] end, rbd_image is None.")
        backup_item.deleted = True
        backup_item.change_status(BACKUP_STATE_DELETED)
        backup_item.save()
        return True

    items = BackupItem.living.filter(chain_id=backup_item.chain_id,
                                     pk__gte=backup_item_id)

    items.update(status=BACKUP_STATE_DELETING)

    cmd = generate_command(backup_item,
                           settings.BACKUP_DELETE_COMMAND,
                           rbd_image=backup_item.rbd_image)

    begin = datetime.datetime.now()
    try:
        result = run_cmd(cmd)
    # Don't delete SoftTimeLimitExceed.
    except (SoftTimeLimitExceeded, Exception):
        items.update(status=BACKUP_STATE_AVAILABLE)
        LOG.exception("Backup item delete error, apply [%s] seconds. %s",
                      time_since(begin), backup_item)
        return False

    duration = time_since(begin)
    is_network_error = isinstance(result, NetworkError)

    # 2 means image snap is deleted.
    if is_network_error or result.return_code not in (0, 2):

        items.update(status=BACKUP_STATE_AVAILABLE)

        if is_network_error:
            LOG.critical("Fabric Error. Cannot connect to host")
        else:
            LOG.info("BackupItem [delete] failed, Return Code: %s, "
                     "apply [%s] seconds. %s",
                     result.return_code, duration, backup_item)

        return False

    items.update(status=BACKUP_STATE_DELETED, deleted=True)
    LOG.info("BackupItem [delete] end, apply [%s] seconds. %s",
             duration, backup_item)

    return True
