#!/usr/bin/env python
# coding=utf-8

from django.utils.translation import ugettext_lazy as _


class ResourceType(object):
    CPU = 'cpu'
    MEM = 'memory'
    VOLUME = 'volume'
    FLOATING = 'floating_ip'
    BANDWIDTH = 'bandwidth'
    TRAFFIC = 'traffic'

    choices = (
        (CPU, _("CPU")),
        (MEM, _("Memory")),
        (VOLUME, _("Volume")),
        (FLOATING, _("Floating IP")),
        (BANDWIDTH, _("Band Width")),
        (TRAFFIC, _("Traffic")),
    )

    label_values = dict(choices)

    @classmethod
    def get_text(cls, value):
        return cls.label_values[value]


class BillResourceType(object):

    INSTANCE = 'instance'
    FLOATING = 'floating_ip'
    VOLUME = 'volume'

    choices = (
        (INSTANCE, _("Instance")),
        (FLOATING, _("Floating IP")),
        (VOLUME, _("Volume")),
    )
    label_values = dict(choices)

    @classmethod
    def get_text(cls, value):
        return cls.label_values[value]

    @classmethod
    def get_type_by_resource(cls, resource):

        clazz_name = resource.__class__.__name__

        if clazz_name == 'Instance':
            return cls.INSTANCE

        if clazz_name == 'Volume':
            return cls.VOLUME

        if clazz_name == 'Floating':
            return cls.FLOATING

        return None


class PriceType(object):

    NORMAL = 'normal'
    DIFF = 'diff'
    LINEAR = 'linear'

    choices = (
        (NORMAL, _("Normal")),
        (DIFF, _("Differential")),
        (LINEAR, _("Linear")),
    )


class PayType(object):

    HOUR = 'hour'
    MONTH = 'month'
    YEAR = 'year'

    choices = (
        (HOUR, _("Charge By Hour")),
        (MONTH, _("Charge By Month")),
        (YEAR, _("Charge By Year")),
    )
