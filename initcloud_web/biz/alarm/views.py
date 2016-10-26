#-*-coding-utf-8-*-

# Author Yang

from datetime import datetime
import logging

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import check_password

from biz.account.settings import QUOTA_ITEM, NotificationLevel
from biz.alarm.models import Alarm 
from biz.alarm.serializer import AlarmSerializer
from biz.alarm.utils import * 
from biz.idc.models import DataCenter, UserDataCenter
from biz.common.pagination import PagePagination
from biz.common.decorators import require_POST, require_GET
from biz.common.utils import retrieve_params, fail
from biz.workflow.models import Step
from cloud.tasks import (link_user_to_dc_task, send_notifications,
                         send_notifications_by_data_center)
from frontend.forms import CloudUserCreateFormWithoutCapatcha

from biz.instance.models import Instance
from biz.instance.serializer import InstanceSerializer
LOG = logging.getLogger(__name__)
from cloud.api import ceilometer
import traceback
from cloud.cloud_utils import create_rc_by_instance, create_rc_by_dc, create_rc_by_udc
from cloud.alarm_task import (alarm_create_task)


from django.db.models import Q



class AlarmList(generics.ListAPIView):
    LOG.info("--------------------- alarm list ------------------------")
    queryset = Alarm.objects.all().filter(deleted=False)
    #LOG.info()
    #LOG.info("--------- Queryset is --------------" + str(queryset)) 
    #serializer_class = AlarmSerializer(queryset, many = True)
    def list(self, request):
	try:
	    udc_id = request.session["UDC_ID"]
	    queryset = self.get_queryset().filter(
		user=request.user, user_data_center__pk=udc_id)
	    serializer = AlarmSerializer(queryset, many=True)
            LOG.info("------------------serializer -----------------")
	    LOG.info("***************** serializer.data " + str(serializer.data))
            return Response(serializer.data)
            #return Response()
        except Exception as e:
            LOG.exception(e)
            return Response()


@require_POST
def create_alarm(request):
    LOG.info(request.data)
    try:
        serializer = AlarmSerializer(data=request.data, context={"request": request})
	#LOG.info(serializer)
	if serializer.is_valid():
            alarmname = request.DATA.get("alarmname")
            alarm_notification = request.DATA.get("alarm_notification")
            LOG.info("******* alarmname is ********" + str(alarmname))
            LOG.info("******* alarm_notification is ********" + str(alarm_notification))
            threshold = request.DATA.get("threshold")
            comparison_operator = request.DATA.get("comparison_operstor")
            meter_name = request.DATA.get("meter_name")
	    alarm = serializer.save(alarmname=alarmname, alarm_ins_id = '', resource_id = '', resource_name = '', alarm_notification = alarm_notification)
	    #LOG.info(serializer.data)
	    #LOG.info("````````````````````` ALARM `````````````````````````````")
	    try:
	        #alarm_create_task.delay(alarm) 
	        alarm_create_task(alarm) 
	    except:
		traceback.print_exc()
            return Response({'success': True, "msg": _('Alarm is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Alarm data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:

        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create alarm for unknown reason.')})



@api_view(["POST"])
def delete_alarms(request):
    #ids = request.data.getlist('ids[]')
    err = False
    ids = request.data.get("ids[]")
    #LOG.info(ids)
    alarms = Alarm.objects.filter(id=ids)
    LOG.info("---------------- alarms are -------------" + str(alarms))
    for alarm in alarms:
        LOG.info("----------------------------DELETE-------------------")
	LOG.info("---------------- alarm id is ------------------------" + str(alarm.alarm_ins_id))
	rc = create_rc_by_instance(alarm)
        LOG.info("--------------- rc is ------------" + str(rc))
        try:
	    result = ceilometer.alarm_delete(rc, alarm.alarm_ins_id)
	    alarm.delete()
            #LOG.info(ceilometer.alarm_list(rc))
        except:
    	    traceback.print_exc()
	    return Response({'success': False, "msg":_('Fail to Delete Alarm!')})
    return Response({'success': True, "msg": _('Alarms have been deleted!')}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def update(request):
    try:
	LOG.info("---------------------- UPDATE -----------------------")
	#LOG.info(request.data)
	resource_id = request.data.get("resource_id")
	has_resource = request.data.get("has_resource")
	resource_name = request.data.get("resource_name")
	alarmname = request.data.get("alarmname")
        #LOG.info("------------------ ALARM MODAL --------------------")
	update_alarm = Alarm.objects.get(id=request.data.get("id"))
	#LOG.info(update_alarm)
        rc = create_rc_by_instance(update_alarm)
	LOG.info("------------------ RC -----------------------------")
	#LOG.info(rc)
	#threshold_rule = update_alarm.threshold_rule
	#meter_name = update_alarm.meter_name
	#comparison_operator = update_alarm.comparison_operator
	#threshold = update_alarm.threshold
	#statistic = update_alarm.statistic
	#threshold_rule = ceilometer.make_threshold_rule(meter_name, comparison_operator, threshold, statistic = statistic)
        #threshold_rule['query'] = ceilometer.make_query(resource_id = resource_id)
        #LOG.info("------------------ THRESHOLD RULE -------------------------")
	#LOG.info(threshold_rule)
	#LOG.info("------------------ ORIGIN ALARM ---------------------------")
	#LOG.info(ceilometer.alarm_list(rc))
	#LOG.info("------------------ UPDATED ALARM --------------------------")
        resource_list = ["resource_id::" + resource_id]
        LOG.info("------------ resource_list is  -----------" + str(resource_list))
        LOG.info("--------- alarmname is ------------" + str(alarmname))
        name = alarmname + ";" + str(update_alarm.alarm_notification) + ";" + str(resource_id)
        LOG.info("888888")
        homeland = {'name':name, 'query': resource_list}

        LOG.info("*********** befor update the alarm ***********")
	try:
	    #LOG.info(ceilometer.alarm_update_query(rc, update_alarm.alarm_ins_id, alarmname, threshold_rule))
	    ceilometer.alarm_update(rc, update_alarm.alarm_ins_id, **homeland)
            LOG.info("************ after update **************")
	except:
	    traceback.print_exc()
	update_alarm.has_resource = has_resource
	update_alarm.resource_id = resource_id
	update_alarm.alarm_name = alarmname
	update_alarm.resource_name = resource_name
	update_alarm.save()
	#LOG.info("------------------ ALL ALARMS -----------------------------")
	#LOG.info(ceilometer.alarm_list(rc))
 
        return Response(
            {'success': True, "msg": _('Alarm is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:

        return Response({"success": False, "msg": _(
            'Failed to update alarm for unknown reason.')})


@api_view(['POST'])
def update_alarm(request):
    try:

        pk = request.data['id']
        LOG.info("---- alarm pk is --------" + str(pk))

        alarm = Alarm.objects.get(pk=pk)
        LOG.info("ddddddddddddd")
        LOG.info("request.data is" + str(request.data))
        alarm.alarmname = request.data['alarmname']

        LOG.info("dddddddddddd")
        alarm.save()
        #Operation.log(alarm, alarm.name, 'update', udc=alarm.udc,
        #              user=request.user)

        return Response(
            {'success': True, "msg": _('Alarm is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update alarm, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to update alarm for unknown reason.')})

class ResourceList(generics.ListAPIView):
    #LOG.info("--------------------- resource list ------------------------")
    queryset = Instance.objects.all().filter(deleted=False)
    #LOG.info("--------- Queryset is --------------" + str(queryset))
    def list(self, request):
        try:
            udc_id = request.session["UDC_ID"]
            UDC = UserDataCenter.objects.all().filter(user=request.user)[0]
            project_id = UDC.tenant_uuid
            queryset = self.get_queryset().filter(Q(user=request.user, user_data_center__pk=udc_id) |Q(tenant_uuid=project_id))
            serializer = InstanceSerializer(queryset, many=True)
            LOG.info("------------------ RESOURCE  -----------------")
            LOG.info(serializer.data)
            return Response(serializer.data)
        except Exception as e:
            LOG.exception(e)
            return Response()

class MeterList(generics.ListAPIView):
    queryset = UserDataCenter.objects.all()
    def list(self, request):
        try:
            udc_id = request.session["UDC_ID"]
            queryset = self.get_queryset().filter(
                user=request.user, id=udc_id)
            #LOG.info(result)
            result = settings.RESULT
	    return Response(result)
        except Exception as e:
            LOG.exception(e)
            return Response()


@require_GET
def is_alarmname_unique(request):
    alarmname = request.GET['alarmname']
    LOG.info("alarmname is" + str(alarmname))
    return Response(not Alarm.objects.filter(alarmname=alarmname).exists())
