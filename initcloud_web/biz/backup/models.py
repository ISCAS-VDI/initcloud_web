#-*- coding=utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


from biz.instance.models import Instance
from biz.volume.models import Volume
from biz.backup.settings import (BACKUP_TYPE_CHOICES, BACKUP_TYPE_FULL,
                                 BACKUP_STATES, BACKUP_STATE_WAITING,
                                 BACKUP_STATE_PENDING_DELETE,
                                 BACKUP_STATE_RESTORING,
                                 BACKUP_STATE_ERROR,
                                 BACKUP_STATE_PENDING_RESTORE,
                                 BACKUP_STATE_AVAILABLE, BACKUP_STATE_DELETED)
from biz.common.mixins import LivingDeadModel
from biz.common.cached_property import cached_property


class Backup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Name"), max_length=64)
    backup_type = models.IntegerField(_("Back Type"),
                                      choices=BACKUP_TYPE_CHOICES,
                                      default=BACKUP_TYPE_FULL)

    volumes = models.CharField(_("Volumes"), max_length=255,
                               null=True, blank=True, default=None)
    instance = models.IntegerField(_("Instance"), null=True, blank=True,
                                   default=None)

    user_data_center = models.ForeignKey('idc.UserDataCenter')
    user = models.ForeignKey('auth.User')

    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    delete_date = models.DateTimeField(_("Delete Date"), auto_now=True)
    deleted = models.BooleanField(_("Deleted"), default=False)
    status = models.IntegerField(_("Status"), choices=BACKUP_STATES, 
                                 default=BACKUP_STATE_WAITING)

    @property
    def backup_type_desc(self):
        return self.get_backup_type_display()

    @property
    def instance_name(self):
        if self.instance:
            try:
                ins = Instance.objects.get(pk=self.instance)
                return ins.name
            except:
                return '---'
        else:
            return 'N/A'

    @property
    def volume_name(self):
        if not self.instance and self.volumes:
            try:
                vol = Volume.objects.get(pk=self.volumes)
                return vol.name
            except:
                return '---'
        else:
            return 'N/A'

    def mark_delete(self):
        self.status = BACKUP_STATE_PENDING_DELETE
        self.save()
        self.items.all().update(status=BACKUP_STATE_PENDING_DELETE)

    def mark_restore(self, item_id=None):
        self.status = BACKUP_STATE_PENDING_RESTORE
        self.save()
        backup_items = self.items.all()
        if item_id:
            backup_items.filter(pk=item_id).update(status=BACKUP_STATE_PENDING_RESTORE)
        else:
            backup_items.update(status=BACKUP_STATE_PENDING_RESTORE)
    
    def __unicode__(self):
        return u"<Backup ID:%s Name:%s>" % (self.id, self.name)

    class Meta:
        db_table = "backup"
        verbose_name = _("Backup")
        verbose_name_plural = _("Backup")
        ordering = ['-create_date']


class BackupItem(LivingDeadModel):

    name = models.CharField(_("Name"), max_length=64)
    rbd_image = models.CharField(_("RBD Image"), max_length=256, null=True,
                                 default=None)
    disk_usage = models.IntegerField(null=True, default=None)

    # One resource can have multiple backup chain, but only one is the default,
    # all increment backup will be executed on top of the default one.
    is_default = models.BooleanField(_("Default Backup"), default=False)
    is_full = models.BooleanField('Full Backup', default=True)
    progress = models.IntegerField(_("Progress"), default=0)
    parent = models.ForeignKey('self', related_name='+', null=True)
    chain_id = models.IntegerField(default=-1)

    resource_id = models.IntegerField(_("Resource ID"))
    resource_uuid = models.CharField(_("Backend UUID"), max_length=64)
    resource_type = models.CharField(_("Resource"), max_length=64)

    user_data_center = models.ForeignKey('idc.UserDataCenter')
    user = models.ForeignKey('auth.User')

    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    delete_date = models.DateTimeField(_("Delete Date"), null=True)

    deleted = models.BooleanField(_("Deleted"), default=False)
    status = models.IntegerField(_("Status"), choices=BACKUP_STATES, 
                                 default=BACKUP_STATE_WAITING)

    class Meta:
        db_table = "backup_item"
        verbose_name = _("Backup Item")
        verbose_name_plural = _("Backup Item")
        ordering = ['-create_date']

    @classmethod
    def create(cls, resource, name, user, udc, is_full=True):

        # Try to get parent item, if parent is None, then create a full backup
        parent = None if is_full else cls.get_recent_item(resource)
        if parent is None:
            is_full = True
            chain_id = -1
        else:
            chain_id = parent.chain_id

        if isinstance(resource, Instance):
            resource_uuid = resource.uuid
        else:
            resource_uuid = resource.volume_id

        backup_item = BackupItem.objects.create(
            name=name,
            is_full=is_full,
            is_default=is_full,
            parent=parent,
            resource_id=resource.id,
            resource_uuid=resource_uuid,
            resource_type=resource.__class__.__name__,
            user_data_center=udc, user=user,
            chain_id=chain_id)

        # If this is full backup, then set other backup items not default
        if is_full:
            BackupItem.living.filter(resource_id=resource.id, parent=None)\
                .exclude(pk=backup_item.id).update(is_default=False)

            backup_item.chain_id = backup_item.id
            backup_item.save()

        return backup_item

    @classmethod
    def get_recent_item(cls, resource):

        resource_type = resource.__class__.__name__

        items = BackupItem.living.filter(resource_id=resource.id,
                                         resource_type=resource_type,
                                         is_default=True)

        if not items.exists():
            return None

        root = items.order_by('-pk')[0]
        item_chain = BackupItem.living.filter(chain_id=root.id)

        return item_chain.order_by('-pk')[0]

    @classmethod
    def has_error_node_on_default_chain(cls, resource):
        resource_type = resource.__class__.__name__
        items = BackupItem.living.filter(resource_id=resource.id,
                                         resource_type=resource_type,
                                         is_default=True)

        if not items.exists():
            return False

        root = items[0]

        return BackupItem.living.filter(status=BACKUP_STATE_ERROR,
                                        chain_id=root.id).exists()

    @classmethod
    def is_any_unstable(cls, resource_id=None,
                        resource_type=None, resource=None):

        if resource:
            resource_id = resource.id
            resource_type = resource.__class__.__name__

        return BackupItem.living.filter(
            resource_id=resource_id,
            resource_type=resource_type)\
            .exclude(status__in=[BACKUP_STATE_AVAILABLE, BACKUP_STATE_ERROR])\
            .exists()

    @classmethod
    def is_any_restoring(cls, resource):
        return BackupItem.living.filter(
            resource_id=resource.id,
            resource_type=resource.__class__.__name__,
            status__in=[BACKUP_STATE_PENDING_RESTORE,
                        BACKUP_STATE_RESTORING])\
            .exists()

    @classmethod
    def revoke_default_chain(cls, chain_id):
        cls.living.filter(pk=chain_id).update(is_default=False)

    @classmethod
    def is_any_node_untable(cls, chain_id):
        return BackupItem.living.filter(chain_id=chain_id).exclude(
            status__in=[BACKUP_STATE_ERROR,  BACKUP_STATE_AVAILABLE,
                        BACKUP_STATE_DELETED]).exists()

    @classmethod
    def mark_chain_delete(cls, backup_item):
        BackupItem.living.filter(chain_id=backup_item.chain_id,
                                 pk__gte=backup_item.pk) \
            .update(status=BACKUP_STATE_PENDING_DELETE)

    def change_status(self, status, save=True):
        self.status = status
        if save:
            self.save()

    @property
    def is_instance_backup(self):
        return self.resource_type == Instance.__name__

    @property
    def is_volume_backup(self):
        return self.resource_type == Volume.__name__

    @cached_property
    def resource(self):
        if self.resource_type == Instance.__name__:
            Model = Instance
        else:
            Model = Volume

        return Model.objects.get(pk=self.resource_id)

    @cached_property
    def resource_name(self):
        return self.resource.name

    @property
    def is_chain_stable(self):
        return not self.is_any_node_untable(self.chain_id)

    def __unicode__(self):
        return u"<BackupItem ID:%s Name:%s Type:%s Resource ID:%s>" % (
            self.id, self.name, self.resource_type, self.resource_id)


class BackupLog(models.Model):

    action = models.CharField(max_length=10)
    duration = models.IntegerField(default=0)
    is_success = models.BooleanField(default=False)
    progress = models.IntegerField(default=0)

    item = models.ForeignKey(BackupItem, related_name='logs',
                             related_query_name='log', null=True)
    name = models.CharField(_("Name"), max_length=64, null=True)
    rbd_image = models.CharField(max_length=256, null=True, default=None)
    disk_usage = models.IntegerField(null=True, default=None)

    resource_id = models.IntegerField()
    resource_uuid = models.CharField(max_length=64)
    resource_type = models.CharField(max_length=64)

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)

    class Meta:
        db_table = "backup_log"
        verbose_name = _("Backup Log")
        verbose_name_plural = _("Backup Log")

    @classmethod
    def log_backup(cls, backup_item):
        return cls.objects.create(item=backup_item, name=backup_item.name,
                                  rbd_image=backup_item.rbd_image,
                                  resource_id=backup_item.resource_id,
                                  resource_type=backup_item.resource_type,
                                  resource_uuid=backup_item.resource_uuid,
                                  action='backup')

    @classmethod
    def log_restore(cls, backup_item):
        return cls.objects.create(item=backup_item, name=backup_item.name,
                                  rbd_image=backup_item.rbd_image,
                                  resource_id=backup_item.resource_id,
                                  resource_type=backup_item.resource_type,
                                  resource_uuid=backup_item.resource_uuid,
                                  action='restore')

    @classmethod
    def end_backup(cls, log_id, is_success, disk_usage=None):

        log = cls.objects.get(pk=log_id)
        log.end_time = timezone.now()
        log.duration = (log.end_time - log.start_time).seconds
        log.is_success = is_success

        if is_success:
            log.progress = 100
            log.disk_usage = disk_usage

        log.save()

        return log

    @classmethod
    def end_restore(cls, log_id, is_success):

        log = cls.objects.get(pk=log_id)
        log.end_time = timezone.now()
        log.duration = (log.end_time - log.start_time).seconds
        log.is_success = is_success

        if is_success:
            log.progress = 100
        log.save()
