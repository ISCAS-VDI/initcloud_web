# -*- coding: utf-8 -*-

from rest_framework import serializers

class VDStatusSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=200)
    vm = serializers.CharField(max_length=200)
    ip_addr = serializers.CharField(max_length=200)

