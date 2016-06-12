#-*- coding=utf-8 -*- 

import datetime
import logging
import time

from django.conf import settings

from cloud_utils import create_rc_by_volume
from biz.volume.settings import (VOLUME_STATE_CREATING,
                                 VOLUME_STATE_AVAILABLE,
                                 VOLUME_STATE_ERROR,
                                 VOLUME_STATE_ERROR_DELETING)
from api import cinder
from cinderclient.exceptions import NotFound
from celery import app
from cloud import billing_task
from biz.billing.models import Order
from biz.volume.models import Volume


LOG = logging.getLogger("cloud.tasks")


def volume_get(volume):
    rc = create_rc_by_volume(volume)
    try:
        return cinder.volume_get(rc, volume.volume_id)
    except NotFound:
        return None


@app.task
def volume_create_task(volume, os_volume_type):
    assert volume is not None
    LOG.info('Volume create start, [%s].', volume)
    rc = create_rc_by_volume(volume)
    begin = datetime.datetime.now()
    try:
        result = cinder.volume_create(rc, size=volume.size,
                                      name="Volume-%04d" % volume.id,
                                      description="",
                                      volume_type=os_volume_type)
    except Exception:
        end = datetime.datetime.now()
        LOG.exception("Volume create api call failed, [%s], "
                      "create api apply [%s] seconds.",
                      volume, (end-begin).seconds)
        volume.change_status(VOLUME_STATE_ERROR)
        return False
    else:
        end = datetime.datetime.now()
        LOG.info("Volume create api call succeed, [%s], "
                "create api apply [%s] seconds.",
                    volume, (end-begin).seconds)
        volume.volume_id = result.id
        volume.change_status(VOLUME_STATE_CREATING)

    # sync volume status
    begin = datetime.datetime.now()
    for count in xrange(settings.MAX_COUNT_SYNC * 2):

        time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
        try:
            st = volume_get(volume).status.upper()
        except Exception:
            LOG.exception("Volume create get status api failed, [%s].", volume)
            volume.change_status(VOLUME_STATE_ERROR)
            return False
    
        LOG.info("Volume synchronize status when create, "
                "[Count:%s][%s][status: %s]",
                 count, volume, st)

        end = datetime.datetime.now()
        if st == "AVAILABLE":
            volume.change_status(VOLUME_STATE_AVAILABLE)
            LOG.info("Volume create succeed, [%s]. apply [%s] seconds.",
                     volume, (end - begin).seconds)

            billing_task.charge_resource.delay(volume.id, Volume)
            return True
        elif st == "ERROR":
            volume.change_status(VOLUME_STATE_ERROR)
            LOG.info("Volume create faild, [%s]. apply [%s] seconds.",
                    volume, (end-begin).seconds)
            return False
        elif st == "CREATING":
            pass
    else:
        end = datetime.datetime.now()
        LOG.info("Volume create timeout, [%s]. apply [%s] seconds.",
                    volume, (end-begin).seconds)
        return False


@app.task
def volume_delete_task(volume):
    assert volume is not None
    LOG.info('Volume delete start, [%s].', volume)

    begin = datetime.datetime.now()
    if volume_get(volume) is None:
        volume.fake_delete()
        Order.disable_order_and_bills(volume)
        return False

    try:
        rc = create_rc_by_volume(volume)
        cinder.volume_delete(rc, volume.volume_id)
    except Exception:
        end = datetime.datetime.now() 
        LOG.exception("Volume delete api call failed, [%s], "
                      "apply [%s] seconds.",
                      volume, (end-begin).seconds)
        volume.change_status(VOLUME_STATE_ERROR_DELETING)
        return False
    else:
        end = datetime.datetime.now() 
        LOG.info("Volume delete api call succeed, [%s], "
                      "apply [%s] seconds.",
                      volume, (end-begin).seconds)
        Order.disable_order_and_bills(volume)

    begin = datetime.datetime.now()
    for count in xrange(settings.MAX_COUNT_SYNC * 2):
        time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
        try:
            cinder_volume = volume_get(volume)
        except Exception:
            LOG.exception("Volume get api failed, when sync status, [%s].",
                            volume)
            volume.change_status(VOLUME_STATE_ERROR_DELETING)
            return False

        st = cinder_volume.status.upper() if cinder_volume else "None"
        LOG.info('Volume synchronize status when delete, [Count:%s][%s][Status: %s].',
                    count, volume, st)

        end = datetime.datetime.now() 
        if cinder_volume is None:
            volume.volume_id = None
            volume.fake_delete()
            LOG.info("Volume delete succeed,[%s], apply [%s] seconds.",
                        volume, (end-begin).seconds)
            return True
        elif cinder_volume.status.upper() == 'ERROR_DELETING':
            volume.change_status(VOLUME_STATE_ERROR_DELETING)
            LOG.info("Volume delete failed, [%s], apply [%s] seconds.",
                        volume, (end-begin).seconds)
            return False
    else:
        end = datetime.datetime.now() 
        LOG.info("Volume delete timeout, [%s], apply [%s] seconds.",
            volume, (end-begin).seconds)
        return False
