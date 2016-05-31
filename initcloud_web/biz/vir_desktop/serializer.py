# -*- coding: utf-8 -*-

from rest_framework import serializers

class VDStatusSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    vm = serializers.CharField(max_length=200)

