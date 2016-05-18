#-*-coding=utf-8-*-

import datetime
import logging
import random

from django.conf import settings

from celery import app
from api import keystone
from biz.account.models import Contract
from biz.idc.models import UserDataCenter
from cloud.cloud_utils import create_rc_by_dc
from cloud.network_task import edit_default_security_group

LOG = logging.getLogger("cloud.tasks")


@app.task
def link_user_to_dc_task(user, datacenter):

    if UserDataCenter.objects.filter(
            user=user, data_center=datacenter).exists():
        LOG.info("User[%s] has already registered to data center [%s]",
                 user.username, datacenter.name)
        return True

    rc = create_rc_by_dc(datacenter)
    tenant_name = "%s-%04d" % (settings.OS_NAME_PREFIX, user.id)

    keystone_user = "%s-%04d-%s" % (settings.OS_NAME_PREFIX, user.id,
                                    user.username)

    LOG.info("Begin to register user [%s] in data center [%s]",
             user.username, datacenter.name)

    t = keystone.tenant_create(rc, name=tenant_name,
                               description=user.username)
    LOG.info("User[%s] is registered as tenant[id:%s][name:%s] in "
             "data center [%s]", user.username, t.id, tenant_name,
             datacenter.name)

    pwd = "cloud!@#%s" % random.randrange(100000, 999999)
    u = keystone.user_create(rc, name=keystone_user, email=user.email,
                             password=pwd, project=t.id)

    LOG.info("User[%s] is registered as keystone user[uid:%s] in "
             "data center[%s]", user.username, u.id, datacenter.name)

    roles = keystone.role_list(rc)
    admin_role = filter(lambda r: r.name.lower() == "admin", roles)[0]
    keystone.add_tenant_user_role(rc, project=t.id, user=u.id,
                                  role=admin_role.id)
    LOG.info("Admin role[%s] in tenant[%s] is granted to user[%s]",
             admin_role.id, t.id, user.username)

    udc = UserDataCenter.objects.create(
        data_center=datacenter,
        user=user,
        tenant_name=tenant_name,
        tenant_uuid=t.id,
        keystone_user=keystone_user,
        keystone_password=pwd,
    )

    LOG.info("Register user[%s] to datacenter [udc:%s] successfully",
             user.username, udc.id)
    try:
        edit_default_security_group(user, udc)
    except:
        LOG.exception("Failed to edit default security group for user[%s] in "
                      "data center[%s]", user.username, datacenter.name)

    Contract.objects.create(
        user=user,
        udc=udc,
        name=user.username,
        customer=user.username,
        start_date=datetime.datetime.now(),
        end_date=datetime.datetime.now(),
        deleted=False
    )

    return u

