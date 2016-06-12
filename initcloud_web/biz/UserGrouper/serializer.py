#coding=utf-8

from rest_framework import serializers

from biz.UserGrouper.models import Usergrouper 
from biz.UserGrouper.models import UserGroupRouter
from biz.idc.serializer import DetailedUserDataCenterSerializer

class UsergrouperSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usergrouper 

class UserGroupRouterSerializer(serializers.ModelSerializer):

    class Meta:
	model = UserGroupRouter

class DetailedUsergrouperSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usergrouper 

