#! /usr/bin/env python


import sys
import json
import requests

URL = 'http://192.168.223.108:8081/login'

client = requests.session()

# Retrieve the CSRF token first

# Sets cookie
client.get(URL, verify = False) 
print client.cookies
csrftoken = client.cookies['csrftoken']
print csrftoken

# Authenticate
login_data = dict(username='klkl', password='ydd1121NN', csrfmiddlewaretoken=csrftoken, next='/')
login_return = client.post(URL, data=login_data, headers=dict(Referer=URL))
print "*********** auth status *********"
print login_return.status_code
print "*********** login_return content is *********"
print login_return.content


# Get instances
instances_return = client.get("http://192.168.223.108:8081/api/instances/vdi/")

print "***************** start to get instances *********"
print "*********** return status is " + str(instances_return.status_code)
print "*********** return type   is " + str(instances_return.headers['content-type'])
print "*********** content       is \n" + str(instances_return.content)
