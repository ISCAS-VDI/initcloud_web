#coding=utf-8

from rest_framework import serializers

from biz.policy_neutron.models import Policy_Neutron 

from biz.idc.serializer import DetailedUserDataCenterSerializer

class Policy_NeutronSerializer(serializers.ModelSerializer):

    class Meta:
        model = Policy_Neutron 


class DetailedPolicy_NeutronSerializer(serializers.ModelSerializer):

    class Meta:
        model = Policy_Neutron 

