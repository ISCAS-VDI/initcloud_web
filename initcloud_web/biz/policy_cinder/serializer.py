#coding=utf-8

from rest_framework import serializers

from biz.policy_cinder.models import Policy_Cinder

from biz.idc.serializer import DetailedUserDataCenterSerializer

class Policy_CinderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Policy_Cinder 


class DetailedPolicy_CinderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Policy_Cinder 

