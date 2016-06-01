#!/usr/bin/env python
# coding=utf-8

from django.conf import settings
from django.core.management import BaseCommand

from fabric import tasks
from fabric.api import run
from fabric.api import env
from fabric.network import disconnect_all


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        env.hosts = [settings.BACKUP_RBD_HOST]
        env.passwords = {
            settings.BACKUP_RBD_HOST: settings.BACKUP_RBD_HOST_PWD
        }

        def echo():
            run("echo %(host)s Connected" % env)

        try:
            tasks.execute(echo)
        finally:
            disconnect_all()
