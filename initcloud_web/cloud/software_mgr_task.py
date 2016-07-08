#-*- coding=utf-8 -*- 

import logging, time
from celery import app

from biz.vir_desktop.models import VirDesktopAction

import cloud.api.software_manager.api as mgr

LOG = logging.getLogger(__name__)

# data for testing
soft_list = []
for i in range(20):
    soft_list.append({"name": "software" + str(i)})

# @app.task
def get_available_software():
    # time.sleep(3)
    # return soft_list
    return mgr.get_available_software()

# @app.task
def get_installed_software(addr):
    # time.sleep(3)
    # return soft_list
    return mgr.get_installed_software(addr)

@app.task
def install_software(ids, addrs, softwares):
    try:
        LOG.info("---install_software---: start task")
        mgr.install_software(softwares, addrs)
        # Change the log's status to install OK/Err in autitor DB
        # time.sleep(5)
        for vm in ids:
            VirDesktopAction.objects.filter(id=vm).update(state='setup_ok')
        LOG.info("---install_software---: finish task")
    except Exception, e:
        LOG.info("---install_software---: %s" % e)
        for vm in ids:
            VirDesktopAction.objects.filter(id=vm).update(state='error')
    
    return True

@app.task
def uninstall_software(ids, addrs, softwares):
    try:
        LOG.info("---uninstall_software---: start task")
        mgr.uninstall_software(softwares, addrs)
        # Change the log's status to uninstall OK/Err in autitor DB
        # time.sleep(5)
        for vm in ids:
            VirDesktopAction.objects.filter(id=vm).update(state='remove_ok')
        LOG.info("---uninstall_software---: finish task")
    except Exception, e:
        LOG.info("---uninstall_software---: %s" % e)
        for vm in ids:
            VirDesktopAction.objects.filter(id=vm).update(state='error')
    
    return True

