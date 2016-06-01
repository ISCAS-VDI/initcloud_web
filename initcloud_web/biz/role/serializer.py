#coding=utf-8

from rest_framework import serializers

from biz.role.models import Role 

from biz.idc.serializer import DetailedUserDataCenterSerializer

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role 


class DetailedRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role 

