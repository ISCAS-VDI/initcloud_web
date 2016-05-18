#!/usr/bin/env python
# coding=utf-8

from rest_framework import serializers

from biz.billing.models import PriceRule, Order, Bill


class PriceRuleSerializer(serializers.ModelSerializer):

    resource_type_text = serializers.ReadOnlyField()

    class Meta:
        model = PriceRule


class OrderSerializer(serializers.ModelSerializer):

    from_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    resource_desc = serializers.ReadOnlyField()

    class Meta:
        model = Order


class BillSerializer(serializers.ModelSerializer):

    from_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    cost = serializers.FloatField()
    resource_desc = serializers.ReadOnlyField()

    class Meta:
        model = Bill
