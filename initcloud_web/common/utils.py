#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

import sys
import imp
from datetime import datetime
from importlib import import_module
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status


def retrieve_params(data, *keys):
    return tuple(data[key] for key in keys)


def retrieve_list_params(data, *keys):
    return tuple(data.getlist(key) for key in keys)


def fail(msg='', status=status.HTTP_200_OK):
    return Response({'success': False, 'msg': msg}, status=status)


def success(msg='', status=status.HTTP_200_OK):
    return Response({'success': True, 'msg': msg}, status=status)


def success_with_data(dicts, status=status.HTTP_200_OK):
    if 'success' not in dicts.keys():
        dicts['success'] = True

    return Response(dicts, status=status)


def error(msg=_('Operation failed. Unknown error happened!'),
          status=status.HTTP_500_INTERNAL_SERVER_ERROR):
    return Response({'success': False, 'msg': msg}, status=status)


def generic_autodiscover(module_name):
    """
    I have copy/pasted this code too many times...Dynamically autodiscover a
    particular module_name in a django project's INSTALLED_APPS directories,
    a-la django admin's autodiscover() method.

    Usage:
        generic_autodiscover('commands') <-- find all commands.py and load 'em
    """

    for app in settings.INSTALLED_APPS:
        try:
            import_module(app)
            app_path = sys.modules[app].__path__
        except AttributeError:
            continue

        try:
            imp.find_module(module_name, app_path)
        except ImportError:
            continue
        import_module('%s.%s' % (app, module_name))

def str2dt(date_str, fmt="%Y-%m-%d %H:%M"):
    try:
        return datetime.strptime(date_str, fmt)
    except:
        pass
    return None
