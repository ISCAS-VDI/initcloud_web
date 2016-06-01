#!/usr/bin/env python
# coding=utf-8

import logging

from django.utils import timezone
from biz.billing.models import Bill, Order
from biz.billing.settings import BillResourceType, PayType
from biz.billing import utils

from cloud.celery import app

LOG = logging.getLogger("cloud.tasks")


@app.task
def charge_resource(resource_id, Model):

    resource = Model.objects.get(pk=resource_id)

    LOG.info("Start to create bill for resource: %s", resource)

    try:
        order = Order.living.get(
            resource_id=resource.id,
            resource_type=BillResourceType.get_type_by_resource(resource))
    except Order.DoesNotExist:
        return

    Bill.create(order)

    LOG.info("Bill for resource is created. %s", resource)


@app.task
def charge_one_day_cost():
    # Not useful for now, just try to keep design.

    now = timezone.now()

    if utils.is_start_of_month(now) and utils.is_midnight(now):
        Bill.objects.filter(active=True).update(active=False)

    for order in Order.living.filter(
            enabled=True, pay_type__in=(PayType.MONTH, PayType.YEAR)):

        # If order is expired, disable this order and active bill
        if now > order.end_time:
            order.enabled = False
            order.save()

            Bill.objects.filter(order=order, active=True).update(active=False)
            continue

        # If order is not effective, just skip it.
        if now < order.effective_date:
            continue

        try:
            bill = Bill.objects.get(orde=order, active=True)
        except Bill.DoesNotExist:
            Bill.create(order)
            continue
        else:
            if bill.end_time <= now:
                bill.charge_one_hour_cost(order)


@app.task
def charge_one_hour_cost():

    now = timezone.now().replace(minute=0, second=0)

    # deactivate old bills at start of every month
    if utils.is_start_of_month(now) and utils.is_midnight(now):
        Bill.objects.filter(active=True).update(active=False)

    for order in Order.living.filter(enabled=True, pay_type=PayType.HOUR):

        # If order is not effective, just skip it.
        if now < order.effective_date:
            continue

        try:
            bill = Bill.objects.get(order=order, active=True)
        except Bill.DoesNotExist:
            if Bill.can_bill(order):
                Bill.create(order)
        else:
            if bill.end_time > now:
                continue
            try:
                bill.update_hour_cost_to_now()
            except Exception:
                LOG.exception("Failed to update bill: %s", bill)
