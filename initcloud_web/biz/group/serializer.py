#coding=utf-8

from rest_framework import serializers

from biz.group.models import Group 

from biz.idc.serializer import DetailedUserDataCenterSerializer

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group 


class DetailedGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group 

