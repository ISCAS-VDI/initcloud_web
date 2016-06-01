import uuid
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.db import transaction, connection
from django.utils.translation import ugettext_lazy as _

from biz.billing.settings import (ResourceType, PriceType,
                                  BillResourceType, PayType)
# Create your models here.

from django.db.models import F

from biz.common.mixins import LivingDeadModel
from biz.instance.models import Instance
from biz.volume.models import Volume
from biz.floating.models import Floating
from biz.billing import utils


class PriceRule(models.Model):

    resource_type = models.CharField(_("Resource Type"),
                                     choices=ResourceType.choices,
                                     max_length=20)
    price_type = models.CharField(_("Price Type"),
                                  choices=PriceType.choices,
                                  default=PriceType.NORMAL,
                                  max_length=20)
    hour_price = models.FloatField(_("Hour Price"), default=0.0)
    month_price = models.FloatField(_("Month Price"), default=0.0)
    hour_diff_price = models.FloatField(_("Hour Differential Price"),
                                        default=0.0)
    month_diff_price = models.FloatField(_("Month Differential Price"),
                                         default=0.0)
    resource_flavor_start = models.IntegerField(_("Resource Flavor Start"),
                                                default=1)
    resource_flavor_end = models.IntegerField(_("Resource Flavor End"),
                                              default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        db_table = "price_rule"
        verbose_name = _("Price Rule")
        verbose_name_plural = _("Price Rules")

    @property
    def resource_type_text(self):
        return  ResourceType.get_text(self.resource_type)

    @classmethod
    def get_price(cls, resource_type, resource_flavor):

        prices = cls.objects.filter(resource_type=resource_type,
                                    resource_flavor_start__lte=resource_flavor)\
            .order_by('-resource_flavor_start')

        if prices.exists():
            return prices[0]
        else:
            return None

    def get_hour_price(self, flavor):

        final_price = self.hour_price

        if self.price_type == PriceType.DIFF:
            diff = flavor - self.resource_flavor_start
            final_price += diff * self.hour_diff_price

        return final_price

    def get_month_price(self, flavor):

        final_price = self.month_price

        if self.price_type == PriceType.DIFF:
            diff = flavor - self.resource_flavor_start
            final_price += diff * self.month_diff_price

        return final_price


class Order(LivingDeadModel):

    order_id = models.CharField(max_length=64)
    resource_id = models.IntegerField()
    resource_type = models.CharField(max_length=20,
                                     choices=BillResourceType.choices)
    pay_type = models.CharField(choices=PayType.choices, max_length=10)
    pay_num = models.IntegerField(default=1)

    enabled = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    from_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, default=None)
    # Effective_date is the day when order should go into effect
    effective_date = models.DateTimeField(auto_now_add=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True, auto_now=True)

    user_data_center = models.ForeignKey('idc.UserDataCenter')
    user = models.ForeignKey('auth.User')

    class Meta:
        db_table = "resource_order"
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    @classmethod
    def create(cls, resource, pay_type, pay_num):

        from_time = timezone.now()

        if pay_type == 'hour':
            end_time = None
        elif pay_type == 'month':
            end_time = from_time + timedelta(days=30 * pay_num)
        else:
            end_time = from_time + timedelta(days=365 * pay_num)

        resource_type = BillResourceType.get_type_by_resource(resource)

        return cls.objects.create(order_id=(uuid.uuid1()),
                                  resource_id=resource.id,
                                  resource_type=resource_type,
                                  from_time=from_time, end_time=end_time,
                                  pay_type=pay_type, pay_num=pay_num,
                                  user=resource.user,
                                  user_data_center=resource.user_data_center)

    @classmethod
    def for_instance(cls, instance, pay_type, pay_num):

        order = cls.create(instance, pay_type, pay_num)

        BillItem.objects.create(order=order,
                                resource_type=ResourceType.CPU,
                                resource_flavor=instance.cpu)

        BillItem.objects.create(order=order,
                                resource_type=ResourceType.MEM,
                                resource_flavor=instance.memory)

    @classmethod
    def for_volume(cls, volume, pay_type,  pay_num):

        order = cls.create(volume, pay_type, pay_num)

        BillItem.objects.create(order=order,
                                resource_type=ResourceType.CPU,
                                resource_flavor=1)

    @classmethod
    def for_floating(cls, floating, pay_type, pay_num):

        order = cls.create(floating, pay_type, pay_num)

        BillItem.objects.create(order=order,
                                resource_type=ResourceType.FLOATING,
                                resource_flavor=1)

        BillItem.objects.create(order=order,
                                resource_type=ResourceType.FLOATING,
                                resource_flavor=floating.bandwidth)

    @classmethod
    def disable_order_and_bills(cls, resource):
        resource_type = BillResourceType.get_type_by_resource(resource)

        cls.living.filter(resource_id=resource.id,
                          resource_type=resource_type,
                          enabled=True).update(enabled=False,
                                               end_time=timezone.now())

        Bill.living.filter(resource_id=resource.id,
                           resource_type=resource_type,
                           active=True).update(active=False)

    def get_price(self):

        price = 0.0

        for item in self.items.all():

            price_rule = PriceRule.get_price(
                resource_type=item.resource_type,
                resource_flavor=item.resource_flavor)

            if price_rule is None:
                continue

            if self.pay_type == 'hour':
                price += price_rule.get_hour_price(item.resource_flavor)
            else:
                price += price_rule.get_month_price(item.resource_flavor)

        return price

    def get_day_price(self):

        price = 0.0

        for item in self.items.all():

            price_rule = PriceRule.get_price(
                resource_type=item.resource_type,
                resource_flavor=item.resource_flavor)

            if price_rule is None:
                continue

            if self.pay_type == 'hour':
                price += price_rule.get_hour_price(item.resource_flavor) * 24
            else:
                price += (price_rule.get_hour_price(item.resource_flavor) / 30)

        return price

    @property
    def resource_desc(self):

        if self.resource_type == BillResourceType.INSTANCE:
            return Instance.objects.get(pk=self.resource_id).name
        elif self.resource_type == BillResourceType.VOLUME:
            return Volume.objects.get(pk=self.resource_id).name
        elif self.resource_type == BillResourceType.FLOATING:
            return Floating.objects.get(pk=self.resource_id).workflow_info
        else:
            return None


class BillItem(LivingDeadModel):

    order = models.ForeignKey(Order, related_name='items',
                              related_query_name='item')
    resource_type = models.CharField(_("Resource Type"),
                                     choices=ResourceType.choices,
                                     max_length=20)
    resource_flavor = models.IntegerField(_("Resource Flavor"))
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "bill_item"
        verbose_name = _("Bill Item")
        verbose_name_plural = _("Bill Items")


class Bill(LivingDeadModel):

    order = models.ForeignKey(Order)
    resource_id = models.IntegerField()
    resource_type = models.CharField(max_length=20)
    pay_type = models.CharField(choices=PayType.choices, max_length=10)
    pay_num = models.IntegerField(default=1)
    cost = models.DecimalField(default=0.0, max_digits=13, decimal_places=4)
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    user = models.ForeignKey('auth.User')
    from_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True, auto_now=True)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "bill"
        verbose_name = _("Bill")
        verbose_name_plural = _("Bill")

    @staticmethod
    def can_bill(order):
        resource = utils.get_resource(order.resource_id, order.resource_type)
        return resource and resource.can_bill()

    @classmethod
    def end_active_bill(cls, resource, force=True):
        resource_type = BillResourceType.get_type_by_resource(resource)

        if resource_type is None:
            raise ValueError("Don't support this kind of resource: %s"
                             % resource.__class__.__name__)

        queryset = cls.objects.filter(resource_id=resource.id,
                                      resource_type=resource_type,
                                      active=True)
        if force:
            queryset.update(active=False)
            return

        queryset.filter(pay_type=PayType.HOUR)

    @classmethod
    def create(cls, order):

        from_time = timezone.now()

        if order.pay_type == PayType.HOUR:
            end_time = from_time.replace(minute=0, second=0)
            end_time += timedelta(hours=1)
            price = order.get_price()
        else:
            end_time = from_time.replace(hour=0, minute=0, second=0)
            price = order.get_day_price()
            end_time += timedelta(days=1)

        bill = cls.objects.create(order=order, resource_id=order.resource_id,
                                  resource_type=order.resource_type,
                                  pay_type=order.pay_type,
                                  pay_num=order.pay_num,
                                  from_time=from_time,
                                  end_time=end_time,
                                  cost=utils.to_decimal(price, 2),
                                  user=order.user,
                                  user_data_center=order.user_data_center)

        BillLog.log(None, bill, price)

    @classmethod
    def increment_cost(cls, pk, cost, end_time):

        with transaction.atomic():
            bill = cls.objects.select_for_update().get(pk=pk)
            bill.cost += cost
            bill.end_time = end_time
            bill.save(update_fields=['cost', 'end_time'])
        return bill

    def charge_one_day_cost(self, order):

        price = order.get_day_price()

        self.end_time = self.end_time + timedelta(days=1)
        self.cost += price
        self.save()

    def charge_one_hour_cost(self, order):

        price = order.get_price()

        self.end_time = self.end_time + timedelta(hours=1)
        self.cost += price
        self.save()

    def update_hour_cost_to_now(self):
        now = timezone.now().replace(minute=0, second=0)
        one_hour_later = now + timedelta(hours=1)

        if one_hour_later < self.end_time:
            return

        price = self.order.get_price()
        delta = (one_hour_later - self.end_time)
        cost = delta.days * 24 * price
        cost += (delta.seconds / 3600) * price

        updated_bill = Bill.increment_cost(self.id, utils.to_decimal(cost, 4),
                                           one_hour_later)

        BillLog.log(self, updated_bill, price)

    @property
    def resource_desc(self):

        if self.resource_type == BillResourceType.INSTANCE:
            return Instance.objects.get(pk=self.resource_id).name
        elif self.resource_type == BillResourceType.VOLUME:
            return Volume.objects.get(pk=self.resource_id).name
        elif self.resource_type == BillResourceType.FLOATING:
            return Floating.objects.get(pk=self.resource_id).workflow_info
        else:
            return None

    def __unicode__(self):
        return "<Bill ID:%s Resource ID:%s Resource Type: %s>" \
               % (self.id, self.resource_id, self.resource_type)


class BillLog(models.Model):

    order = models.ForeignKey(Order)
    bill = models.ForeignKey(Bill)
    resource_id = models.IntegerField()
    resource_type = models.CharField(max_length=20)
    old_cost = models.DecimalField(default=0.0, max_digits=13, decimal_places=4)
    new_cost = models.DecimalField(default=0.0, max_digits=13, decimal_places=4)
    price = models.DecimalField(default=0.0, max_digits=13, decimal_places=4)
    old_end_time = models.DateTimeField(default=None, null=True)
    new_end_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bill_log"
        verbose_name = _("Bill Log")
        verbose_name_plural = _("Bill Logs")

    @classmethod
    def log(cls, old_bill, new_bill, price):

        old_cost = 0.0 if old_bill is None else old_bill.cost
        old_end_time = None if old_bill is None else old_bill.end_time

        cls.objects.create(order=new_bill.order, bill=new_bill,
                           resource_id=new_bill.resource_id,
                           resource_type=new_bill.resource_type,
                           old_cost=old_cost, new_cost=new_bill.cost,
                           old_end_time=old_end_time,
                           new_end_time=new_bill.end_time,
                           price=price)
