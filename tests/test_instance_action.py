#! /usr/bin/env python


import sys
import json
import requests

URL = 'http://192.168.223.108:8081/login'

client = requests.session()

# Retrieve the CSRF token first

# Sets cookie
client.get(URL, verify = False) 
csrftoken = client.cookies['csrftoken']
print "******** csrftoken **********"
print csrftoken

# Authenticate
login_data = dict(username='klkl', password='ydd1121NN', csrfmiddlewaretoken=csrftoken, next='/')
login_return = client.post(URL, data=login_data, headers=dict(Referer=URL))
print "*********** auth status *********"
print login_return.status_code


# instance action 
"""
supported action = ["reboot", "power_on", "power_off", "vnc_console", "bind_floating", "unbind_floating", "terminate", "attach_volume", "detach_volume", "launch"]
"""
#params: instance internal id, action choose from the above supported action.
payload = {"instance":22, "action":"terminate"}
# request ulr with get method
URL_ = "http://192.168.223.108:8081/api/instances/vdi_action/"
instances_return = client.get(URL_, params=payload)

print "***************** start to get instances *********"
print "*********** return status is " + str(instances_return.status_code)
print "*********** return type   is " + str(instances_return.headers['content-type'])
# content value
"""
content's format is {"status":6,"OPERATION_STATUS":1}.
---------------------------------------------
OPERATION STATUS has the following values.

OPERATION_SUCCESS = 1
OPERATION_FAILED = 0
OPERATION_FORBID = 2
---------------------------------------------

Status has the following values.

INSTANCE_STATE_WAITING = 0
INSTANCE_STATE_RUNNING = 1
INSTANCE_STATE_BOOTING = 2
INSTANCE_STATE_REBOOTING = 3
INSTANCE_STATE_PAUSED = 4
INSTANCE_STATE_POWEROFF = 5
INSTANCE_STATE_SHUTTING_DOWN = 6
INSTANCE_STATE_DEPLOYING = 7
INSTANCE_STATE_DEPLOY_FAILED = 8
INSTANCE_STATE_LOCKED = 9
INSTANCE_STATE_DELETE = 10
INSTANCE_STATE_ERROR = 11
INSTANCE_STATE_BACKUPING = 12
INSTANCE_STATE_RESTORING = 13
INSTANCE_STATE_RESIZING = 14
INSTANCE_STATE_EXPIRED = 15
INSTANCE_STATE_DELETING = 16
INSTANCE_STATE_APPLYING = 17
INSTANCE_STATE_REJECTED = 18
------------------------------------------

"""
print "*********** content       is \n" + str(instances_return.content)

