# -*- coding:utf-8 -*-

from rest_framework import serializers

from biz.heat.models import Heat 

from biz.idc.serializer import DetailedUserDataCenterSerializer

class HeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Heat 


class DetailedHeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Heat 

