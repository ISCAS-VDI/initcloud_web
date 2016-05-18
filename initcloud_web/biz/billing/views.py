from django.shortcuts import render

# Create your views here.

import logging
from datetime import datetime

from rest_framework import generics
from rest_framework.response import Response

from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum, Count

from biz.common.decorators import require_POST, require_GET
from biz.common.utils import fail, success, error
from biz.common.pagination import PagePagination
from biz.billing.serializer import (PriceRuleSerializer, OrderSerializer,
                                    BillSerializer)
from biz.billing.models import PriceRule, Order, Bill

LOG = logging.getLogger(__name__)


@require_GET
def price_rules(request):

    resource_type = request.query_params['resource_type']
    rules = PriceRule.objects.filter(resource_type=resource_type)\
        .order_by('resource_flavor_start')
    serializer = PriceRuleSerializer(rules, many=True)

    return Response(serializer.data)


@require_POST
def create_price_rule(request):

    serializer = PriceRuleSerializer(data=request.data)

    if not serializer.is_valid():
        return fail(_("Data is not valid."))

    serializer.save()

    return success(_("Price is created."))


@require_POST
def update_price_rule(request):

    pk = request.data['id']
    rule = PriceRule.objects.get(pk=pk)
    serializer = PriceRuleSerializer(data=request.data, instance=rule)

    if not serializer.is_valid():
        return fail(_("Data is not valid."))

    serializer.save()

    return success(_("Price is created."))


@require_POST
def delete_rules(request):
    ids = request.data.getlist('ids[]')
    PriceRule.objects.filter(pk__in=ids).delete()
    return success(_('Prices have been deleted!'))


class OrderList(generics.ListAPIView):
    queryset = Order.living.all()
    serializer_class = OrderSerializer
    pagination_class = PagePagination

    def get_queryset(self):

        request = self.request
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status = request.query_params.get('status')
        resource_type = request.query_params.get('resource_type')

        queryset = super(OrderList, self).get_queryset()
        queryset = queryset.filter(
            user=request.user, user_data_center__id=request.session["UDC_ID"])

        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        if start_date:
            queryset = queryset.filter(create_time__gte=start_date)

        if end_date:
            queryset = queryset.filter(
                create_time__lte=format_date(end_date, 'end'))

        if status == 'enabled':
            queryset = queryset.filter(enabled=True)

        if status == 'disabled':
            queryset = queryset.filter(enabled=False)

        return queryset


class BillList(generics.ListAPIView):
    queryset = Bill.living.all()
    serializer_class = BillSerializer
    pagination_class = PagePagination

    def get_queryset(self):

        request = self.request
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        resource_type = request.query_params.get('resource_type')

        queryset = super(BillList, self).get_queryset()
        queryset = queryset.filter(
            user=request.user,
            user_data_center__id=request.session["UDC_ID"])

        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        if start_date:
            queryset = queryset.filter(
                from_time__gte=format_date(start_date, 'start'))

        if end_date:
            queryset = queryset.filter(
                end_time__lte=format_date(end_date, 'end'))

        return queryset


@require_GET
def bill_overview(request):

    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    queryset = Bill.objects.all()

    if start_date:
        queryset = queryset.filter(
            from_time__gte=format_date(start_date, 'start'))

    if end_date:
        queryset = queryset.filter(
            end_time__lte=format_date(end_date, 'end'))

    overviews = queryset.values('resource_type')\
        .annotate(total_cost=Sum('cost'))

    for overview in overviews:
        overview['num'] = queryset.\
            filter(resource_type=overview['resource_type']).\
            values('resource_type', 'resource_id').distinct().count()

    return Response(overviews)


def _query_start_and_end(queryset, start_date, end_date):

    if start_date:
        queryset = queryset.filter(
            from_time__gte=format_date(start_date, 'start'))

    if end_date:
        queryset = queryset.filter(
            end_time__lte=format_date(end_date, 'end'))

    return queryset


def format_date(date_string, start_or_end=None):
    date = datetime.strptime(date_string, '%Y-%m-%d')

    if start_or_end is None:
        return date
    elif start_or_end == 'start':
        return date.replace(hour=0, minute=0)
    else:
        return date.replace(hour=23, minute=59)


