#-*-coding-utf-8-*-

# Author Yang

from datetime import datetime
import logging
import json

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
from biz.account.models import UserProxy
from biz.account.serializer import UserSerializer
from biz.UserGrouper.models import Usergrouper
from biz.UserGrouper.serializer import UsergrouperSerializer
from biz.UserGrouper.utils import * 
from biz.idc.models import DataCenter
from biz.role.models import Role
from biz.role.serializer import RoleSerializer
from biz.common.pagination import PagePagination
from biz.common.decorators import require_POST, require_GET
from biz.common.utils import retrieve_params, fail
from biz.workflow.models import Step
from cloud.tasks import (link_user_to_dc_task, send_notifications,
                         send_notifications_by_data_center)
from frontend.forms import CloudUserCreateFormWithoutCapatcha

from biz.UserGrouper.models import Usergrouper
from biz.UserGrouper.models import UserGroupRouter
from biz.UserGrouper.serializer import UserGroupRouterSerializer
import traceback
import json
LOG = logging.getLogger(__name__)


class UsergrouperList(generics.ListAPIView):
    #LOG.info("--------- I am UserGrouper list in UsergrouperList ----------")
    #queryset = Usergrouper.objects.all()
    #LOG.info("--------- Queryset is --------------" + str(queryset)) 
    #serializer_class = UsergrouperSerializer
    def list(self, request):
	LOG.info("111111111111111111111111111")
	groups= Usergrouper.objects.all().filter(deleted=False)
	serializer = UsergrouperSerializer(groups, many = True)
	return Response(serializer.data)

@require_POST
def UserCheckList(request):
	LOG.info("**************************************")
	LOG.info(request.data)
	group = Usergrouper.objects.all().filter(id = request.data.get("id"))
	router = UserGroupRouter.objects.all().filter(group = group)
	LOG.info(router)
	#try:
	#    serializer = UserGroupRouterSerializer(router, many=True)
	#    LOG.info(serializer.data)
	#except:
	#    traceback.print_exc()
	#return Response(serializer.data)
	result = []
	for r in router:
	    if not r.deleted:
		checked = True
                result.append({"id":r.id,"user_id":r.user.id,"user_name":r.user.username,"group":r.group.id,"checked":checked})
	    else:
	        result.append({"id":r.id,"user_id":r.user.id,"user_name":r.user.username,"group":r.group.id})
	return Response(result)
	#return Response(json.dumps(result))

@require_POST
def UserView(request):
        LOG.info(request.data)
	LOG.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^6")
	try:
        	group = Usergrouper.objects.all().filter(id = request.data.get("id"))
        	router = UserGroupRouter.objects.all().filter(group = group, deleted = False)
	except:
		traceback.print_exc()
        LOG.info(router)
        result = []
        for r in router:
            result.append({"id":r.id,"user_id":r.user.id,"user_name":r.user.username,"group":r.group.id})
        return Response(result)



@require_POST
def create_UserGrouper(request):
    LOG.info(request.data)
    try:
        serializer = UsergrouperSerializer(data=request.data, context={"request": request})
	if serializer.is_valid():
	    LOG.info(serializer.data)
            grouper = serializer.save(param_char1 = '', param_char2 = '')
	    LOG.info("----------- NEW CREATED --------------------")
	    LOG.info(grouper)
	    LOG.info(type(grouper))
	    users = User.objects.all().filter(is_active = True)
	    for user in users:
                LOG.info("----------- A USER ---------------")
                LOG.info(user)
		LOG.info("----------  A ROUTER -------------")
                LOG.info(UserGroupRouter.objects.create(user = user, group = grouper))
	    LOG.info(UserGroupRouter.objects.all().filter(group = grouper))

            return Response({'success': True, "msg": _('Usergrouper is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Usergrouper data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:

        LOG.error("Failed to create flavor, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create UserGrouper for unknown reason.')})


@api_view(["POST"])
def delete_UserGroupers(request):
    ids = request.data.getlist('ids[]')
    group = Usergrouper.objects.filter(pk__in=ids)
    #LOG.info(group)
    for router in UserGroupRouter.objects.all().filter(group = Usergrouper.objects.filter(pk__in=ids)):
#	LOG.info(router)
	router.delete()
    #LOG.info(UserGroupRouter.objects.all().filter(group = Usergrouper.objects.filter(pk__in=ids)))
    Usergrouper.objects.filter(pk__in=ids).delete()
    return Response({'success': True, "msg": _('Usergroupers have been deleted!')}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def update_UserGrouper(request):
    LOG.info(request.data)
    #all_users = User.objects.all().filter(is_active = True)
    routers = UserGroupRouter.objects.all().filter(group=request.data.get("group"))
    try:
	users = request.data.get("users")
	#group = request.data.get("group")
	users = users.split(",")
	for router in routers:
	    #route_user = User.objects.all().filter(id = user)
	    #route_group = Usergrouper.objects.filter(id = group)
	    #router = UserGroupRouter.objects.all().filter(group=route_group, user=route_user)
	    if unicode(router.user.id) in users:
		LOG.info(router)
	    	router.deleted = False
	    else:
		router.deleted = True
	    router.save()
	    #LOG.info(router)
	    #LOG.info(router.deleted)
        #pk = request.data['id']
        #LOG.info("---- UserGrouper pk is --------" + str(pk))

        #UserGrouper = Usergrouper.objects.get(pk=pk)
        #UserGrouper.UserGroupername = request.data['UserGroupername']

        #UserGrouper.save()
        #Operation.log(UserGrouper, UserGrouper.name, 'update', udc=UserGrouper.udc,
        #              user=request.user)

        return Response(
            {'success': True, "msg": _('Usergrouper is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update UserGrouper, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to update UserGrouper for unknown reason.')})


@require_GET
def is_UserGroupername_unique(request):
    UserGroupername = request.GET['UserGroupername']
    LOG.info("UserGroupername is" + str(UserGroupername))
    return Response(not Usergrouper.objects.filter(UserGroupername=UserGroupername).exists())


@require_POST
def add_group_user_view(request):
    LOG.info("request.data is" + str(request.data))

    user_ids = request.data['user_ids']
    user_ids_str = str(user_ids)
    user_ids_list = []
    if ',' not in user_ids_str:
        user_ids_list.append(int(user_ids_str))
    else:
        user_ids_list = user_ids_str.split(",")
    groupid = request.data['group_id'][0]
    LOG.info("********** group_id is **********" + str(groupid))
    LOG.info("********** user_ids_list  is **********" + str(user_ids_list))
    for userid in user_ids_list:
        LOG.info("user_id is" + str(userid))
        if UserGroupRouter.objects.filter(user_id=int(userid), group_id=int(groupid), deleted=False):
            continue
        LOG.info("not exists")
        try:
            usergrouper = UserGroupRouter(user_id=int(userid), group_id=int(groupid), deleted=False) 
            LOG.info("begin to save")
            usergrouper.save()
        except:
            raise
    return Response({'success': True, "msg": _('Usergrouper is updated successfully!')})

@require_POST
def delete_group_user_view(request):
    LOG.info("request.data is" + str(request.data))

    user_id = request.data['user_id']
    group_id = request.data['group_id']

    LOG.info("********** user_id *********" + str(user_id))
    LOG.info("********** group_id *********" + str(group_id))
    try:
        usergrouper = UserGroupRouter.objects.get(user_id=int(user_id), group_id=int(group_id), deleted=False) 
        LOG.info("begin to delete")
        usergrouper.delete()
    except:
        raise
    return Response({'success': True, "msg": _('Usergrouper is updated successfully!')})


class user_grouper_detail_view(generics.ListAPIView):

    def list(self, request, group_id):
        LOG.info("c-cpu")
        LOG.info("group_id is" + str(group_id))
       
        userids_set = UserGroupRouter.objects.filter(
            deleted=False, group_id=group_id)
            #user_data_center=request.session["UDC_ID"])

        LOG.info("********* userids_set is *******" + str(userids_set))
        userids = []
        for user_id in userids_set:
            LOG.info("*********** user_id is **********" + str(user_id.user.id))
            #user = User.objects.get(pk=user_id.user.id)
            userids.append(user_id.user.id)
            #data['username'] = user.username
        LOG.info("****** userids ******" + str(userids))
        queryset = UserProxy.normal_users.filter(pk__in=userids)
        LOG.info("********* queryset **********" + str(queryset))
        serializer = UserSerializer(queryset, many=True)
        LOG.info("********* serializer **********" + str(serializer))
        return Response(serializer.data)
