#coding=utf-8

from rest_framework import serializers

from biz.policy_nova.models import Policy_Nova 

from biz.idc.serializer import DetailedUserDataCenterSerializer

class Policy_NovaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Policy_Nova 


class DetailedPolicy_NovaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Policy_Nova 

