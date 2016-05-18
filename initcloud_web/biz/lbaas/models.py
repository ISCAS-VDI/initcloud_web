from django.db import models
from django.utils.translation import ugettext_lazy as _
from .settings import (POOL_CREATING, POOL_STATES,
                       PROTOCOL_CHOICES, LB_METHOD_CHOICES, ADMIN_STATE_UP,
                       MONITOR_TYPE, PROVIDER_CHOICES, SESSION_PER_CHOICES,
                       SESSION_PER_CHOICES_DICT, LB_METHOD_DICT, PROTOCOL_MAP)
# Create your models here.

from biz.common.mixins import LivingDeadModel


class BalancerPool(LivingDeadModel):
    id = models.AutoField(primary_key=True)

    pool_uuid = models.CharField(_("Pool UUID"), null=True, blank=True, max_length=40)
    name = models.CharField(_("Pool name"), null=False, blank=False, max_length=64)
    description = models.CharField(_("Description"), null=False, blank=True, max_length=128)
    subnet = models.ForeignKey('network.Subnet')
    protocol = models.IntegerField(_("protocol"), choices=PROTOCOL_CHOICES)
    lb_method = models.IntegerField(_("Lb method"), choices=LB_METHOD_CHOICES)
    provider = models.IntegerField(_("Provider"), default=0, choices=PROVIDER_CHOICES)
    admin_state_up = models.BooleanField(_("Admin state up"), default=True, choices=ADMIN_STATE_UP)
    vip = models.ForeignKey("lbaas.BalancerVIP",  null=True, blank=True, related_name="vip_obj")

    status = models.IntegerField(_("Status"), default=POOL_CREATING, choices=POOL_STATES)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    deleted = models.BooleanField(_("Deleted"), default=False)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')

    class Meta:
        db_table = "lbaas_pool"
        verbose_name = _("BalancerPool")
        verbose_name_plural = _("BalancerPool")

    def __unicode__(self):
        if self.pool_uuid:
            return u'id:%s, name:%s, uuid:%s' % (self.id, self.name,
                                                 self.pool_uuid)
        else:
            return u'id:%s, name:%s' % (self.id, self.name)

    def change_status(self, status, save=True):
        self.status = status
        if save:
            self.save()

    @property
    def protocol_text(self):
        return PROTOCOL_MAP[self.protocol]

    @property
    def lb_method_text(self):
        return LB_METHOD_DICT[self.lb_method]


class BalancerMember(models.Model):
    id = models.AutoField(primary_key=True)
    pool = models.ForeignKey('lbaas.BalancerPool', null=True, blank=True)
    instance = models.ForeignKey("instance.Instance", null=True, blank=True)

    member_uuid = models.CharField(_("Member_UUID"), null=True, blank=True, max_length=40)
    address = models.CharField(_("Address"), null=True, blank=True, max_length=20)
    protocol_port = models.IntegerField(_('Protocol port'), null=True, blank=True)
    weight = models.IntegerField(_('Weight'))
    admin_state_up = models.BooleanField(_("Admin state up"), default=True, choices=ADMIN_STATE_UP)

    status = models.IntegerField(_("Status"), default=POOL_CREATING, choices=POOL_STATES)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    deleted = models.BooleanField(_("Deleted"), default=False)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')

    class Meta:
        db_table = 'lbaas_member'
        verbose_name = _("BalancerMember")
        verbose_name_plural = _("BalancerMember")

    def __unicode__(self):
        if self.member_uuid:
            return u'id:%s, uuid:%s' % (self.id,  self.member_uuid)
        else:
            return u'id:%s' % self.id


class BalancerVIP(models.Model):
    id = models.AutoField(primary_key=True)
    vip_uuid = models.CharField(_('VIP_uuid'), null=False, blank=True, max_length=40)

    name = models.CharField(_("Name"), max_length=64)
    # todo: add default value
    description = models.CharField(_("Description"), blank=True,
                                   max_length=128,  default='')

    subnet = models.ForeignKey("network.Subnet", null=True, blank=True)
    public_address = models.CharField(_('Address'), null=True, blank=True, max_length=20)
    address = models.CharField(_('Address'), null=True, blank=True, max_length=20)
    protocol = models.IntegerField(_("Protocol"), choices=PROTOCOL_CHOICES)
    protocol_port = models.IntegerField(_('Protocol port'))

    port_id = models.CharField(_("Port id"), null=True, blank=True, max_length=40)

    # todo: add default value for no session choice
    session_persistence = models.IntegerField(_('Session Persistence'),
                                              choices=SESSION_PER_CHOICES,
                                              default=-1)
    connection_limit = models.IntegerField(_("Connection limit"), default=-1)
    admin_state_up = models.BooleanField(_("Admin state up"), default=True, choices=ADMIN_STATE_UP)
    status = models.IntegerField(_("Status"), default=POOL_CREATING, choices=POOL_STATES)

    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    deleted = models.BooleanField(_("Deleted"), default=False)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')

    class Meta:
        db_table = 'lbaas_vip'
        verbose_name = _("BalancerVIP")
        verbose_name_plural = _("BalancerVIP")

    @property
    def session_persistence_desc(self):
        return SESSION_PER_CHOICES_DICT.get(self.session_persistence, '')

    @property
    def has_session_persistence(self):
        # 0: source_ip
        # 1: http_cookie
        # 2: app_cookie
        return self.session_persistence in (0, 1, 2)

    def __unicode__(self):
        if self.vip_uuid:
            return u'id:%s, name:%s, uuid:%s' % (self.id, self.name,
                                                 self.vip_uuid)
        else:
            return u'id:%s, name:%s' % (self.id, self.name)


class BalancerMonitor(models.Model):
    id = models.AutoField(primary_key=True)
    monitor_uuid = models.CharField(_('Monitor uuid'), null=False, blank=True,
                                    max_length=40)
    name = models.CharField(_("Monitor name"), null=True, blank=True,
                            max_length=128)
    type = models.IntegerField(_("Type"), choices=MONITOR_TYPE)
    delay = models.IntegerField(_("Delay"), null=True)
    timeout = models.IntegerField(_("Timeout"), null=True)
    max_retries = models.IntegerField(_("Max retries"))
    http_method = models.CharField(_("Http method"), default="GET", null=True,
                                   blank=True, max_length=10)
    url_path = models.CharField(_("Url path"), default="/",  null=True,
                                blank=True, max_length=80)
    expected_codes = models.CharField(_("Expected codes"), default="200",
                                      null=True, blank=True, max_length=128)
    admin_state_up = models.BooleanField(_("Admin state up"), default=True,
                                         choices=ADMIN_STATE_UP)

    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    deleted = models.BooleanField(_("Deleted"), default=False)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')

    @property
    def balancers_name(self):
        query_set = BalancerPoolMonitor.objects.filter(monitor=self.id)
        desc = ""
        if len(query_set) > 0:
            desc = ",".join(b.pool.name for b in query_set)
        return desc

    class Meta:
        db_table = 'lbaas_monitor'
        verbose_name = _("BalancerMonitor")
        verbose_name_plural = _("BalancerMonitor")

    def __unicode__(self):
        if self.monitor_uuid:
            return u'id:%s, name:%s, uuid:%s' % (self.id, self.name,
                                                 self.monitor_uuid)
        else:
            return u'id:%s, name:%s' % (self.id, self.name)


class BalancerPoolMonitor(models.Model):
    id = models.AutoField(primary_key=True)
    monitor = models.ForeignKey("lbaas.BalancerMonitor", related_name="monitor_re")
    pool = models.ForeignKey("lbaas.BalancerPool", related_name="pool_re")

    class Meta:
        db_table = 'lbaas_pool_monitor'
        verbose_name = _("BalancerPoolMonitor")
        verbose_name_plural = _("BalancerPoolMonitor")

