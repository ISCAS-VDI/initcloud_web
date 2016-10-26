#-*- coding=utf-8 -*- 

import datetime
import logging
import time
import ast

from django.conf import settings

from celery import app

from biz.instance.settings import (INSTANCE_STATE_RUNNING,
                                   INSTANCE_STATE_BOOTING, INSTANCE_STATE_ERROR,
                                   INSTANCE_STATE_DELETE,
                                   INSTANCE_STATE_POWEROFF)
from biz.instance.models import Instance
from biz.heat.models import Heat

from biz.volume.settings import (VOLUME_STATE_AVAILABLE,
                                 VOLUME_STATE_IN_USE, VOLUME_STATE_ERROR)
from biz.image.settings import WINDOWS, LINUX

from cloud_utils import create_rc_by_instance, create_rc_by_dc, get_admin_client, get_nova_admin
from cloud.api import heat as heatclient
from cloud.api import nova
from network_task import make_sure_default_private_network
from cloud import volume_task, billing_task


from biz.idc.models import DataCenter, UserDataCenter
from cloud.cloud_utils import (create_rc_by_network, create_rc_by_subnet,
                         create_rc_by_router, create_rc_by_floating,
                         create_rc_by_security,  create_rc_by_udc)


from api import nova
from api import neutron


LOG = logging.getLogger(__name__)

@app.task
def stack_create_sync_status_task(stack_id, user, tenant_uuid, heat, retry_count=1):
    assert stack_id
    retry_count += 1

    stack_ = None
    begin = datetime.datetime.now()
    for count in xrange(settings.MAX_COUNT_SYNC):
        stack_ = heatclient.stack_get(user, stack_id)
        status = stack_.status.upper() if stack_ else u"None"

        LOG.info("*** stack_ is ***" + str(stack_))
        stack_name = stack_.stack_name
        LOG.info("*** status is ***" + str(status))

        if status == "COMPLETE":
            heat.stack_id = stack_id
            heat.deploy_status = True
            heat.stack_name = stack_name

            if stack_:

                id_ = 0
                UDC = UserDataCenter.objects.all().filter(user=user)[0]
                LOG.info("4")
                rc = create_rc_by_udc(UDC)
                stack = stack_
                resources = None
                try:
                    LOG.info("9999")
                    stack_identifier = '%s/%s' % (stack.stack_name, stack.id)
                    resources = heatclient.resources_list(user, stack_identifier)
                    LOG.info("66666")
                    LOG.info('got resources %s' % resources)
                    # The stack id is needed to generate the resource URL.
                    for r in resources:
                        r.stack_id = stack.id
                except Exception:
                    pass

                console_dic = {}

                if not resources:
                    break 
                for resource in resources:
                    LOG.info("resources is oooooooooooooooooooooo" +str(resource))

                    if resource.resource_type == "OS::Heat::ResourceGroup":
                        LOG.info("resource type is resource group")
                        stack_ = None
                        try:
                            stack_ = heatclientstack_get(user, resource.physical_resource_id)
                        except:
                            pass
                        if not stack_:
                            break 
                        resources_ = None
                        try:
                            LOG.info("9999")
                            stack_identifier_ = '%s/%s' % (stack_.stack_name, stack_.id)
                            resources_ = heatclient.resources_list(user, stack_identifier_)
                            LOG.info("66666")
                            LOG.info('got resources %s' % resources_)
                            # The stack id is needed to generate the resource URL.
                            for r in resources_:
                                r.stack_id = stack_.id
                        except Exception:
                            pass
                        if resources_ == None:
                            break 
                        for re in resources_:
                            console_url_ = None
                            instance_ = None
                            LOG.info("instance id in group is" + str(re.physical_resource_id))
                            try:
                                instance_ = nova.server_get(rc, re.physical_resource_id)
                                #console_url_ = project_console.get_console(request, 'VNC', instance_)
                                console_url_ = "http://test"
                            except Exception:
                                pass
                            if instance_:
                                data.append({"id": instance_.id, "servicename": order_heatname, "instancename": instance_.name, "console": console_url_})

                                id_ = id_ + 1


                    else:

                        LOG.info("resource_tpye is server")
                        console_url = None
                        instance = None

                        try:
                            LOG.info("*** resource.physical_resource_id ***" + str(resource.physical_resource_id))
                            instance = nova.server_get(rc, resource.physical_resource_id)
                            LOG.info("*** instance is ***" + str(instance))
                            console_url = "http://test"#project_console.get_console(request, 'VNC', instance)
                        except Exception:
                            pass
                        #console_dic[resource.logical_resource_id] = console_url
                        if instance:
                            LOG.info("*** start to append data")
                            LOG.info("*** instance is ***" + str(instance))
                            LOG.info("servicename " + str(instance.name))
                            id_ = id_ + 1
                            LOG.info("*** id_ is ***" + str(id_))
                            instance_id = instance.id
                            instance_name = instance.name
                            private_ip = None
                            public_ip = None
                            try:
                                LOG.info("*** stack_name is ****" + str(stack_name))
                                LOG.info("*** stack_id is ****" + str(stack_id))
                                LOG.info("*** user is ****" + str(user))
                                LOG.info("*** instance_id is ***" + str(instance_id))
                                LOG.info("*** instance_name is ****" + str(instance_name))
                                addresses = instance.addresses
                                LOG.info("*** addresses are ***" + str(addresses))
                                for key, value in addresses.items():
                                    LOG.info("key is" + str(key))
                                    LOG.info("value is" + str(value))
                                    for v in value:
                                        if v['OS-EXT-IPS:type'] == "fixed":
                                            LOG.info("*** get  fixed ip ****")
                                            private_ip = v['addr']
                                        if v['OS-EXT-IPS:type'] == "floating":
                                            LOG.info("*** get public ip ****")
                                            public_ip = v['addr']
                                LOG.info("*****")
                                flavor = instance.flavor
                                LOG.info("*****")
                                flavor_id = flavor['id']
                                LOG.info("*****")
                                novaAdmin = get_nova_admin(instance)
                                LOG.info("*****")
                                try:
                                    flavor = novaAdmin.flavors.get(flavor_id)
                                except Exception:
                                    flavor = {}
                                    raise
                                real_flavor = flavor.to_dict()
                                LOG.info("** real_flavor is **" + str(real_flavor))
                                LOG.info("***** flavor is " + str(real_flavor))
                                #flavor_ = flavor['flavor']
                                LOG.info("*****")
                                cpu = real_flavor['vcpus']
                                LOG.info("*****")
                                disk = real_flavor['disk']
                                LOG.info("*****")
                                memory = real_flavor['ram']
                                LOG.info("*** cpu is ***" +str(cpu))
                                LOG.info("*** disk is ***" +str(disk))
                                LOG.info("*** memory is ***" +str(memory))

                                LOG.info("*** private_ip is ***" + str(private_ip))
                                LOG.info("*** public_ip is ***" + str(public_ip))
                                LOG.info("*** flavor is ***" + str(flavor))
                                user_data_center = UserDataCenter.objects.get(user=user)
                                user_data_center_id = user_data_center.id
                                LOG.info("*** user_data_center_id ***" + str(user_data_center_id))
                                LOG.info("*** tenant_uuid ***" + str(tenant_uuid))
                                instance_save = Instance(name=instance_name, status=1, user=user, uuid=instance_id, cpu=cpu, memory=memory, sys_disk=disk, network_id=1, flavor_id=flavor_id, private_ip=private_ip, public_ip=public_ip,  user_data_center_id=user_data_center_id, policy=1, tenant_uuid=tenant_uuid)
                                LOG.info("******************")
                                instance_save.save()

                            except:
                                raise

            LOG.info("*** instances of this stack are ****" + str(id_))
            heat.save()
            LOG.info("cccccccc")
            break

        if status == "FAILED":
            heat.stack_id = None
            heat.deploy_status = False
            heat.stack_status_reason = stack_.stack_status_reason
            heat.save()
            LOG.info("*** stack_status_reason is ***" + str(stack_.stack_status_reason))
            break
        if status == "IN_PROGRESS":
            continue

        time.sleep(settings.INSTANCE_SYNC_INTERVAL_SECOND)
    else:
        end = datetime.datetime.now()
        if retry_count <= 3:
            LOG.warn(u"Instance create timeout")
            stack_create_sync_status_task.delay(stack_id, user, tenant_uuid, heat)
            return False
        else:
            LOG.error(u"Stack create timeout")
            return False
    return True

@app.task
def deploy_stack(user, heat, stack_name, timeout_mins, disable_rollback, password, parameters, template, tenant_uuid):
    LOG.info("start to post data to celery")
    LOG.info("*** user is ***" + str(user))
    LOG.info("*** parameters is ***" + str(parameters))
    LOG.info("*** template is ***" + str(template))


    params_list = parameters
    params_list = str(params_list)
    params_str = params_list.encode("utf8")
    LOG.info("params_str's type is" + str(type(params_str)))
    params_list = ast.literal_eval(params_str)
    meta = {
          'stack_name': stack_name,
          'timeout_mins': timeout_mins,
          'disable_rollback': disable_rollback,
          'password': password,
          'parameters': params_list,
          'template': template,
    }
    LOG.info("ddddd")
    stack = heatclient.stack_create(user, **meta)
    LOG.info("ddd")
    stack_id = stack['stack']['id']
    LOG.info(stack_id)
    stack_create_sync_status_task.delay(stack_id, user, tenant_uuid, heat)
    return stack
