#-*-coding=utf-8-*- 

import datetime
import logging

from celery import app
from cloud_utils import create_rc_by_balancer_pool, \
    create_rc_by_balancer_vip, create_rc_by_balancer_member,\
    create_rc_by_balancer_monitor

from biz.lbaas.settings import POOL_ACTIVE, POOL_ERROR, POOL_DOWN
from biz.lbaas.models import BalancerMember, BalancerPoolMonitor, BalancerVIP
from biz.floating.models import Floating

from api import lbaas, network
import neutronclient

LOG = logging.getLogger("cloud.tasks")


def pool_get(pool=None):
    rc = create_rc_by_balancer_pool(pool)
    try:
        p = lbaas.pool_get(rc,pool_id=pool.pool_uuid)
        return p
    except Exception as e:
        LOG.exception(e)
        return False


def pool_delete(pool=None):
    rc = create_rc_by_balancer_pool(pool)
    lbaas.pool_delete(rc, pool.pool_uuid)


def pool_member_update(member):
    rc = create_rc_by_balancer_member(member)
    LOG.info("Begin to update balancer member[%s]", member)
    try:
        params = {"member": {"weight": member.weight}}
        lbaas.member_update(rc, member_id=member.member_uuid, **params)
    except Exception:
        LOG.exception("Failed to update balancer member[%s]", member)
        return False
    else:
        LOG.info("Balancer member[%s] is updated.", member)
        return True


def pool_member_get(member=None):
    rc = create_rc_by_balancer_member(member)
    try:
        m = lbaas.member_get(rc,member_id=member.member_uuid)
        return m
    except Exception as e:
        LOG.exception(e)
        return e


def pool_member_delete(member=None):
    rc = create_rc_by_balancer_member(member)
    return lbaas.member_delete(rc,member.member_uuid)


def pool_vip_create(vip, pool_uuid):
    rc = create_rc_by_balancer_vip(vip)
    if vip.has_session_persistence:
        session_persistence = {'type': vip.session_persistence_desc}
    else:
        session_persistence = {}

    name = "balancer-vip-%04d%04d" % (vip.user.id, vip.id)

    v = lbaas.vip_create(rc, name=name,
                         description=vip.description,
                         subnet_id=vip.subnet.subnet_id,
                         protocol_port=vip.protocol_port,
                         protocol=vip.get_protocol_display(),
                         pool_id=pool_uuid,
                         session_persistence=session_persistence,
                         admin_state_up=vip.admin_state_up,
                         connection_limit=vip.connection_limit,
                         address=vip.address)
    return v


def pool_vip_update(vip=None):
    rc = create_rc_by_balancer_vip(vip)

    if vip.has_session_persistence:
        session_persistence = {'type': vip.session_persistence_desc}
    else:
        session_persistence = {}

    params = {"vip": {
        'description': vip.description,
        'session_persistence': session_persistence}}

    return lbaas.vip_update(rc, vip_id=vip.vip_uuid, **params)


def pool_vip_get(vip=None):
    rc = create_rc_by_balancer_vip(vip)
    try:
        v = lbaas.vip_get(rc,vip.vip_uuid)
        return v
    except Exception as e:
        LOG.exception(e)
        return False


def vip_associate_floating_ip(vip, float_ip_uuid):

    assert vip
    assert float_ip_uuid

    rc = create_rc_by_balancer_vip(vip)

    LOG.info("Begin to associate floating ip [%s] to vip[%s]",
             float_ip_uuid, vip)
    try:
        port_id = "%s_%s" % (vip.port_id, vip.address)
        network.floating_ip_associate(rc, float_ip_uuid, port_id)
    except Exception:
        LOG.exception("Failed to associate floating ip [%s] to vip[%s]",
                      float_ip_uuid, vip)
        return False
    else:
        LOG.info("Floating ip [%s] is associated to vip[%s]",
                 float_ip_uuid, vip)
        return True


def vip_disassociate_floating_ip(vip, float_ip_uuid):
    rc = create_rc_by_balancer_vip(vip)

    LOG.info("Begin to disassociate floating ip[%s] from vip[%s]",
             float_ip_uuid, vip)
    try:
        network.floating_ip_disassociate(rc, float_ip_uuid, vip.port_id)
    except Exception:
        LOG.exception("Failed to disassociate floating ip[%s] from vip[%s]",
                      float_ip_uuid, vip)
        return False
    else:
        LOG.info("Floating ip[%s] is disassociated from vip[%s]",
                 float_ip_uuid, vip)
        return True


def pool_monitor_create(monitor=None):
    rc = create_rc_by_balancer_monitor(monitor)
    LOG.info("Begin to create pool monitor[%s]", monitor)
    try:
        m = lbaas.pool_health_monitor_create(
            rc, type=monitor.get_type_display(), delay=monitor.delay,
            timeout=monitor.timeout, max_retries=monitor.max_retries,
            admin_state_up=monitor.admin_state_up,
            http_method=monitor.http_method, url_path=monitor.url_path,
            expected_codes=monitor.expected_codes)
    except Exception:
        LOG.exception("Failed to create pool monitor [%s]", monitor)
        return False
    else:
        monitor.monitor_uuid = m.id
        monitor.save()
        LOG.info("Pool monitor [%s] is created", monitor)
        return True


def pool_monitor_update(monitor=None):
    rc = create_rc_by_balancer_monitor(monitor)
    LOG.info("Begin to update pool monitor[%s]", monitor)
    try:
        params = {"health_monitor": {
                  "delay": monitor.delay,
                  "timeout": monitor.timeout,
                  "max_retries": monitor.max_retries}}
        lbaas.pool_health_monitor_update(rc, monitor_id=monitor.monitor_uuid,
                                         **params)
    except:
        LOG.exception("Failed to update pool monitor[%s]", monitor)
        return False
    else:
        LOG.info("Pool monitor[%s] is updated", monitor)
        return True


def pool_monitor_delete(monitor):
    rc = create_rc_by_balancer_monitor(monitor)
    LOG.info("Begin to delete pool monitor[%s]", monitor)
    try:
        lbaas.pool_health_monitor_delete(rc, mon_id=monitor.monitor_uuid)
    except neutronclient.common.exceptions.NotFound:
        pass
    except Exception:
        LOG.exception("Failed to delete pool monitor[%s]", monitor)
        return False

    LOG.info("Pool monitor[%s] is deleted", monitor)
    monitor.deleted = True
    monitor.save()
    return True


def pool_monitor_association_create(pool, monitor):
    rc = create_rc_by_balancer_pool(pool)
    LOG.info("Begin to associate pool monitor[%s] with pool[%s]", monitor, pool)
    try:
        lbaas.pool_monitor_association_create(rc, pool_id=pool.pool_uuid,
                                              monitor_id=monitor.monitor_uuid)
    except Exception:
        LOG.exception("Failed to associate pool monitor[%s] with pool[%s]",
                      monitor, pool)
        return False
    else:
        BalancerPoolMonitor.objects.create(pool=pool, monitor=monitor)
        LOG.info("Pool monitor[%s] is associated to pool[%s]", monitor, pool)
        return True


def pool_monitor_association_delete(pool, monitor):
    rc = create_rc_by_balancer_pool(pool)
    LOG.info("Begin to disassociate pool monitor[%s] from pool[%s]",
             monitor, pool)
    try:
        lbaas.pool_monitor_association_delete(rc, pool_id=pool.pool_uuid,
                                              monitor_id=monitor.monitor_uuid)

    except neutronclient.common.exceptions.NotFound:
        pass
    except Exception:
        LOG.exception("Begin to disassociate pool monitor[%s] from pool[%s]",
                      monitor, pool)
        return False

    LOG.info("Pool monitor[%s] is disassociated from pool[%s]",
             monitor, pool)
    BalancerPoolMonitor.objects.filter(pool=pool, monitor=monitor).delete()
    return True


@app.task
def pool_create_task(pool):

    assert pool is not None

    LOG.info("Begin to create balancer pool[%s]", pool)

    try:
        rc = create_rc_by_balancer_pool(pool)
        name = "balancer-pool-%04d%04d" % (pool.user.id, pool.id)
        lbaas_pool = lbaas.pool_create(
            rc, name=name, description=pool.description,
            subnet_id=pool.subnet.subnet_id,
            protocol=pool.protocol_text,
            lb_method=pool.lb_method_text,
            admin_state_up=pool.admin_state_up,
            provider=pool.get_provider_display())

    except Exception:
        LOG.exception("Failed to create balancer pool[%s]", pool)
        pool.status = POOL_ERROR
        pool.save()
        return False
    else:
        LOG.info("Balancer pool[%s] is created. uuid[%s]", pool,
                 lbaas_pool.id)
        pool.pool_uuid = lbaas_pool.id
        pool.status = POOL_ACTIVE
        pool.save()
        return True


@app.task
def pool_update_task(pool):

    assert pool is not None

    LOG.info("Begin to update balancer pool[%s][%s].", pool.id, pool.name)

    rc = create_rc_by_balancer_pool(pool)
    try:
        params = {'pool': {'description': pool.description,
                           'lb_method': pool.get_lb_method_display()}}

        update_result = lbaas.pool_update(rc, pool_id=pool.pool_uuid, **params)
    except Exception:
        LOG.exception("Failed to update balancer pool[%s][%s].",
                      pool.id, pool.name)
        pool.status = POOL_ERROR
        pool.save()
        return False
    else:
        LOG.info("Balancer[%s][%s] pool is updated. uuid[%s]",
                 pool.id, pool.name, update_result.id)
        pool.status = POOL_ACTIVE
        pool.save()
        return True


@app.task
def pool_delete_task(pool):
    assert pool is not None

    LOG.info("Begin to delete balancer pool id[%s],name[%s], uuid[%s]",
             pool.id, pool.name, pool.pool_uuid)

    for member in BalancerMember.objects.filter(deleted=False, pool=pool):
        try:
            pool_member_delete(member)
        except neutronclient.common.exceptions.NotFound:
            pass
        except Exception:
            # Even member not deleted successfully, when delete pool in
            # openstack, members will be deleted
            LOG.exception("Failed to delete pool member[%s] of pool [%s][%s]",
                          member.id, pool.id, pool.name)

        member.deleted = True
        member.save()
        LOG.info("Pool member[%s] of pool[%s][%s] is deleted",
                 member.id, pool.id, pool.name)

    vip = pool.vip
    if vip:
        if not pool_vip_delete_task(vip, pool):
            LOG.error("Failed to delete vip of pool. vip[%s], pool[%s]",
                      vip, pool)
            return False

    for pool_monitor in BalancerPoolMonitor.objects.filter(pool=pool.id):
        # monitors in openstack will be deleted automatically, so no need to
        # delete it manually
        pool_monitor.delete()
        LOG.info("Pool monitor[%s] is deleted", pool_monitor.id)

    if pool.pool_uuid:

        try:
            rc = create_rc_by_balancer_pool(pool)
            lbaas.pool_delete(rc, pool.pool_uuid)
        except neutronclient.common.exceptions.NotFound:
            pass
        except Exception:
            LOG.exception("Failed to delete balancer pool[id:%s],[uuid:%s]",
                          pool.id, pool.pool_uuid)
            pool.status = POOL_ERROR
            pool.save()
            return False

    pool.pool_uuid = ''
    pool.status = POOL_DOWN
    pool.deleted = True
    pool.save()
    LOG.info("Balancer pool is deleted. Pool: [%s]", pool)
    return True


@app.task
def pool_vip_create_task(vip, pool):
    LOG.info("Begin to create balancer vip[%s] for pool[%s]", vip, pool)

    try:
        v = pool_vip_create(vip, pool.pool_uuid)
    except Exception:
        LOG.exception("Failed to created balancer vip[%s]", vip)
        pool.status = POOL_ACTIVE
        pool.vip = None
        pool.save()
        vip.delete()
        return False
    else:
        LOG.info("Balancer vip is created. vip[%s, uuid:%s]", vip, v.id)
        vip.status = POOL_ACTIVE
        vip.vip_uuid = v.id
        vip.address = v.address
        vip.port_id = v.port_id
        vip.save()
        pool.status = POOL_ACTIVE
        pool.vip = vip
        pool.save()
        return True


@app.task
def pool_vip_update_task(vip):
    assert vip

    LOG.info("Begin to update balancer vip [%s]", vip)
    try:
        v = pool_vip_update(vip)
    except:
        LOG.exception("Failed to update balancer vip[%s]", vip)
        vip.status = POOL_ERROR
        vip.save()
        return False
    else:
        LOG.info("Balancer vip is updated. vip [%s, uuid:%s]", vip, v.id)
        vip.status = POOL_ACTIVE
        vip.save()
        return True


@app.task
def pool_vip_delete_task(vip, pool):

    assert vip

    LOG.info("Begin to delete balancer vip[%s]", vip)
    try:
        rc = create_rc_by_balancer_vip(vip)
        lbaas.vip_delete(rc, vip.vip_uuid)
    except neutronclient.common.exceptions.NotFound:
        pass
    except Exception:
        LOG.exception("Failed to delete balancer vip[%s]", vip)
        vip.status = POOL_ERROR
        vip.save()

        pool.status = POOL_ACTIVE
        pool.save()

        return False

    floating = Floating.get_lbaas_ip(resource_id=pool.id)
    if floating:
        floating.unbind_resource()
    LOG.info("Floating IP of vip is released.")

    pool.vip = None
    pool.save()

    vip.vip_uuid = ''
    vip.deleted = True
    vip.save()
    LOG.info("Balancer vip[%s] is deleted.", vip)

    return True


@app.task
def pool_member_create_task(member):

    assert member

    LOG.info("Begin to create balancer member[%s]", member)

    try:
        rc = create_rc_by_balancer_member(member)
        m = lbaas.member_create(rc, pool_id=member.pool.pool_uuid,
                                address=member.instance.private_ip,
                                protocol_port=member.protocol_port,
                                weight=member.weight,
                                admin_state_up=member.admin_state_up)

    except Exception:
        LOG.exception("Failed to create balancer member[%s]", member)
        member.status = POOL_ERROR
        member.save()
        return False
    else:
        LOG.info("Balancer member[%s, uuid:%s] is created", member, m.id)
        member.member_uuid = m.id
        member.status = POOL_ACTIVE
        member.address = m.address
        member.save()
        return True


@app.task
def pool_member_delete_task(member):
    assert member

    LOG.info("Begin to delete balancer member[%s]", member)
    try:
        pool_member_delete(member)
    except neutronclient.common.exceptions.NotFound:
        pass
    except:
        LOG.exception("Failed to delete balancer member[%s]", member)
        member.status = POOL_ERROR
        member.save()
        return False

    LOG.info("Balancer member[%s] is deleted", member)
    member.member_uuid = ''
    member.deleted = True
    member.save()
    return True
