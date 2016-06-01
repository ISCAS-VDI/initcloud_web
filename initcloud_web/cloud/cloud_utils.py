#-*-coding=utf-8-*-

from keystoneclient.v2_0 import client
from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient.client import Client
from django.conf import settings



RC_ENV = {
    "username": "username",
    "password": "password",
    "tenant_name": "tenant_name",
    "auth_url": "auth_url",
}


def _create_rc(obj=None):
    rc = RC_ENV.copy()

    rc["username"] = obj.user_data_center.keystone_user
    rc["password"] = obj.user_data_center.keystone_password
    rc["tenant_name"] = obj.user_data_center.tenant_name
    rc["tenant_uuid"] = obj.user_data_center.tenant_uuid
    rc["auth_url"] = obj.user_data_center.data_center.auth_url

    return rc


def get_nova_admin(instance):
    auth = v2.Password(auth_url=settings.AUTH_URL,
                           username=settings.ADMIN_NAME,
                           password=settings.ADMIN_PASS,
                           tenant_name=settings.ADMIN_TENANT_NAME)
    sess = session.Session(auth=auth)
    #this should read from settings
    novaClient = Client(settings.NOVA_VERSION, session=sess)
    return novaClient


def get_admin_client(instance=None):
    admin_client = client.Client(token=settings.ADMIN_TOKEN, endpoint=settings.ENDPOINT)

    return admin_client

def create_rc_by_instance(instance=None):
    return _create_rc(instance)


def create_rc_by_network(network=None):
    return _create_rc(network)


def create_rc_by_subnet(subnet=None):
    return _create_rc(subnet)


def create_rc_by_router(router=None):
    return _create_rc(router)


def create_rc_by_volume(volume=None):
    return _create_rc(volume)


def create_rc_by_floating(floating=None):
    return _create_rc(floating)


def create_rc_by_udc(udc=None):
    rc = RC_ENV.copy()

    rc["username"] = udc.keystone_user
    rc["password"] = udc.keystone_password
    rc["tenant_name"] = udc.tenant_name
    rc["tenant_uuid"] = udc.tenant_uuid
    rc["auth_url"] = udc.data_center.auth_url

    return rc


def create_rc_by_dc(dc=None):
    rc = RC_ENV.copy()

    rc["username"] = dc.user
    rc["password"] = dc.password
    rc["tenant_name"] = dc.project
    rc["auth_url"] = dc.auth_url

    return rc


def create_rc_by_security(firewall=None):
    return _create_rc(firewall)


def create_rc_by_balancer_pool(pool=None):
    return _create_rc(pool)


def create_rc_by_balancer_member(member=None):
    return _create_rc(member)


def create_rc_by_balancer_vip(vip=None):
    return _create_rc(vip)


def create_rc_by_balancer_monitor(monitor=None):
    return _create_rc(monitor)
