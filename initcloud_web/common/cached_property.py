#!/usr/bin/env python
# coding=utf-8

__author__ = 'Daniel Greenfeld'
__email__ = 'pydanny@gmail.com'
__version__ = '1.2.0'
__license__ = 'BSD'

from time import time
import threading
import functools
import weakref
import six


class cached_property(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class threaded_cached_property(object):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        if obj is None:
            return self

        obj_dict = obj.__dict__
        name = self.func.__name__
        with self.lock:
            try:
                # check if the value was computed before the lock was acquired
                return obj_dict[name]
            except KeyError:
                # if not, do the calculation and release the lock
                return obj_dict.setdefault(name, self.func(obj))


class cached_property_with_ttl(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Setting the ttl to a number expresses how long
    the property will last before being timed out.
    """

    def __init__(self, ttl=None):
        if callable(ttl):
            func = ttl
            ttl = None
        else:
            func = None
        self.ttl = ttl
        self._prepare_func(func)

    def __call__(self, func):
        self._prepare_func(func)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        now = time()
        obj_dict = obj.__dict__
        name = self.__name__
        try:
            value, last_updated = obj_dict[name]
        except KeyError:
            pass
        else:
            ttl_expired = self.ttl and self.ttl < now - last_updated
            if not ttl_expired:
                return value

        value = self.func(obj)
        obj_dict[name] = (value, now)
        return value

    def __delete__(self, obj):
        obj.__dict__.pop(self.__name__, None)

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = (value, time())

    def _prepare_func(self, func):
        self.func = func
        if func:
            self.__doc__ = func.__doc__
            self.__name__ = func.__name__
            self.__module__ = func.__module__

# Aliases to make cached_property_with_ttl easier to use
cached_property_ttl = cached_property_with_ttl
timed_cached_property = cached_property_with_ttl


class threaded_cached_property_with_ttl(cached_property_with_ttl):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, ttl=None):
        super(threaded_cached_property_with_ttl, self).__init__(ttl)
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        with self.lock:
            return super(threaded_cached_property_with_ttl, self).__get__(obj,
                                                                          cls)

# Alias to make threaded_cached_property_with_ttl easier to use
threaded_cached_property_ttl = threaded_cached_property_with_ttl
timed_threaded_cached_property = threaded_cached_property_with_ttl


def _try_weakref(arg, remove_callback):
    """Return a weak reference to arg if possible, or arg itself if not."""
    try:
        arg = weakref.ref(arg, remove_callback)
    except TypeError:
        pass
    return arg


def _get_key(args, kwargs, remove_callback):
    """Calculate the cache key, using weak references where possible."""
    weak_args = tuple(_try_weakref(arg, remove_callback) for arg in args)
    weak_kwargs = tuple(sorted(
        (key, _try_weakref(value, remove_callback))
        for (key, value) in six.iteritems(kwargs)))
    return weak_args, weak_kwargs

def memoized_with_ttl(ttl=0):
    """Decorator that caches function calls.
       ttl = 0 will be never expired
    """
    def _wrapped(func):
        cache = {}

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            key = None
            def remove(ref):
                """A callback to remove outdated items from cache."""
                try:
                    del cache[key]
                except KeyError:
                    pass

            key = _get_key(args, kwargs, remove)
            now = time()
            try:
                value, last_updated = cache[key]
                ttl_expired = ttl > 0 and ttl < now - last_updated
                if ttl_expired:
                    value, last_updated  = cache[key] = func(*args, **kwargs), now 
            except KeyError:
                value, last_updated = cache[key] = func(*args, **kwargs), now
            except TypeError:
                print "The key %r is not hashable and cannot be memoized." % key
                value = func(*args, **kwargs)
            return value
        return wrapped
    return _wrapped
