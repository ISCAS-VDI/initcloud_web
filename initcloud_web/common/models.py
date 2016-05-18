#!/usr/bin/env python
# coding=utf-8

from django.db import models
from django.utils import timezone

from django.utils.translation import ugettext_lazy as _


class LivingQuerySet(models.QuerySet):

    def fake_delete(self):
        return self.update(deleted=True, deleted_at=timezone.now())


class LivingManager(models.Manager):

    def get_queryset(self):
        return LivingQuerySet(self.model, using=self._db).filter(deleted=False)

    def get_or_none(self, *args, **kwargs):
        obj = None
        try:
            obj = self.get_queryset().get(*args, **kwargs)
        except models.ObjectDoesNotExist:
            pass

        return obj


class DeletedManager(models.Manager):

    def get_queryset(self):
        return super(DeletedManager, self).get_queryset().filter(deleted=True)


class BaseModel(models.Model):

    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = models.Manager()
    living = LivingManager()
    dead = DeletedManager()

    class Meta:
        abstract = True

    def fake_delete(self):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save()
