#!/usr/bin/env python
# coding=utf-8

from datetime import timedelta
from decimal import Decimal

from biz.instance.models import Instance
from biz.volume.models import Volume
from biz.floating.models import Floating
from biz.billing.settings import BillResourceType


def is_end_of_month(time):
    one_day_later = time + timedelta(days=1)
    return time.date().month != one_day_later.date().month


def is_start_of_month(time):
    return time.date().day == 1


def is_midnight(time):
    return time.time().hour == 0


def get_resource(resource_id, resource_type):
    if resource_type == BillResourceType.INSTANCE:
        return Instance.objects.get(pk=resource_id)
    elif resource_type == BillResourceType.VOLUME:
        return Volume.objects.get(pk=resource_id)
    elif resource_type == BillResourceType.FLOATING:
        return Floating.objects.get(pk=resource_id)
    else:
        return None


def to_decimal(s, precision=8):
    """
    to_decimal('1.2345', 2) => Decimal('1.23')
    to_decimal(1.2345, 2) => Decimal('1.23')
    to_decimal(Decimal('1.2345'), 2) => Decimal('1.23')
    """
    r = pow(10, precision)
    v = s if type(s) is Decimal else Decimal(str(s))
    try:
        return Decimal(int(v * r)) / r
    except:
        return Decimal(s)
