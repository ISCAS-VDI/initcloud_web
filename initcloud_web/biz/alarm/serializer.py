#coding=utf-8

from rest_framework import serializers

from biz.alarm.models import Alarm 
from django.contrib.auth.models import User
from biz.idc.models import UserDataCenter

from biz.idc.serializer import DetailedUserDataCenterSerializer

class AlarmSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              required=False, allow_null=True,
                                              default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(
                queryset=UserDataCenter.objects.all(),  required=False,
                allow_null=True, default=None)
    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user
    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])
    
    class Meta:
        model = Alarm 


class DetailedAlarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alarm 

