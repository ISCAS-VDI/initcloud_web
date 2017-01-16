#!/usr/bin/env python
# coding:utf8

import sys
import os
import re
from optparse import OptionParser
import json
import copy
import yaml
DIRNAME = os.path.abspath(os.path.dirname(__file__))


''' Here is an example of config.yml
ansible_ssh_user: "username"
ansible_ssh_pass: "password"
hosts:
    - "192.168.90.1"
'''


with open(os.path.join(DIRNAME, "config.yml")) as f:
    config = yaml.load(f)


hosts = {
    'all': {
        'hosts': config["hosts"],
    }
}

VARS = {
    "ansible_ssh_host": None,
    "ansible_ssh_user": config["ansible_ssh_user"],
    "ansible_ssh_pass": config["ansible_ssh_pass"],
    "ansible_ssh_port": 5985,
    # "ansible_ssh_port": 5986,
    "ansible_connection": "winrm",
    # "ansible_winrm_server_cert_validation": "ignore",
}


def get_hosts():
    return hosts


def pick_host(name):
    res = copy.deepcopy(VARS)
    res["ansible_ssh_host"] = name
    return res


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        "--list",
        action="store_true",
        dest="list_host",
        default=None,
        help="list hosts"
    )
    parser.add_option(
        "--host",
        dest="host_name",
        help="get info about a HOST",
        metavar="HOST"
    )

    (options, args) = parser.parse_args()

    if options.host_name:
        print(pick_host(options.host_name))
        sys.exit(0)

    if options.list_host:
        print(json.dumps(get_hosts()))
        sys.exit(0)
