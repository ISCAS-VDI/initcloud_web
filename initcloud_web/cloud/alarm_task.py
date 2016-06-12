#-*- coding=utf-8 -*- 

import datetime
import logging
import time

from django.conf import settings
from celery import app
from cloud_utils import create_rc_by_instance, create_rc_by_dc
from api import ceilometer
from biz.alarm.models import Alarm
import traceback
LOG = logging.getLogger(__name__)



#@app.task
def alarm_create_task(alarm, **kwargs):
    assert alarm
    #monitor.save()
    LOG.info("----------------------  CREATE ALARM -----------------")
    rc = create_rc_by_instance(alarm)
    LOG.info("************ rc is *************" + str(rc))
    #LOG.info(monitor)
    #LOG.info(monitor.name)
    #LOG.info(monitor.meter_name)
    #LOG.info(monitor.comparison_operator)
    #LOG.info(monitor.threshold)
    #LOG.info(rc)
    client = ceilometer.ceilometerclient(rc)
    LOG.info("***********" + str(alarm))
    alarm_id = alarm.id
    LOG.info("***********")
    name = alarm.alarmname
    notification = alarm.alarm_notification
    LOG.info("***********" + str(name))
    comparison_operator = alarm.comparison_operator
    LOG.info("***********" + str(comparison_operator))
    threshold = alarm.threshold
    LOG.info("***********" + str(threshold))
    meter_name = alarm.meter_name
    LOG.info("***********" + str(meter_name))
    severity = alarm.severity
    LOG.info("***********" + str(severity))
    alarm_actions = "http://192.168.223.108:8081" 
    LOG.info("***********")
    statistic = alarm.statistic
    LOG.info("*********** statistic is " + str(statistic))
    description = "test"
    project_id = rc['tenant_uuid']
    LOG.info("******** after get project_id *********")
    period = 60
    name = name + ";" + notification
    LOG.info("******** new alarm name is ************" + str(name))
    meta = {"alarm_actions": [settings.ALARM_ACTIONS], "severity": str(severity), "description": "test", "enabled": True, "threshold_rule": {"threshold": int(threshold), "meter_name": meter_name, "period": 60, "statistic": statistic}, "repeat_actions": False, "type": "threshold", "name": name, "comparison_operator": comparison_operator}
    LOG.info("************* befor create alarm ************")
    
    try:
        alarm_to_create = client.alarms.create(**meta)
        LOG.info("************ after alarm create **************")
    except:
        raise
    alarm.alarm_ins_id = alarm_to_create.alarm_id
    #LOG.info(alarm.alarm_ins_id)
    alarm.save()
#    except:
#	traceback.print_exc()
    return True
