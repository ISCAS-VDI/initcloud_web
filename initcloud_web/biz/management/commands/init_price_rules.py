#!/usr/bin/env python
# coding=utf-8

from django.core.management import BaseCommand

from biz.billing.models import PriceRule
from biz.billing.settings import ResourceType, PriceType


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        PriceRule.objects.create(resource_type=ResourceType.CPU,
                                 price_type=PriceType.NORMAL)

        PriceRule.objects.create(resource_type=ResourceType.MEM,
                                 resource_flavor_start=512,
                                 price_type=PriceType.NORMAL)

        PriceRule.objects.create(resource_type=ResourceType.VOLUME,
                                 price_type=PriceType.LINEAR)

        PriceRule.objects.create(resource_type=ResourceType.FLOATING,
                                 price_type=PriceType.LINEAR)

        PriceRule.objects.create(resource_type=ResourceType.BANDWIDTH,
                                 price_type=PriceType.NORMAL)

        PriceRule.objects.create(resource_type=ResourceType.TRAFFIC,
                                 price_type=PriceType.LINEAR)
