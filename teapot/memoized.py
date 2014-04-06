"""
A Memoized metaclass.
"""

import functools
from contextlib import contextmanager

from .error import TeapotError
from .log import Highlight as hl


class Memoized(type):

    """
    A Memoized type.
    """

    DEFAULT_MEMOIZATION_KEY = 'name'
    DEFAULT_PROPAGATE_MEMOIZATION_KEY = False

    def __new__(cls, name, bases, attrs):

        @classmethod
        def get_instance(mycls, key, default=None):
            return mycls._INSTANCES.get(key, default)

        @classmethod
        def get_instances(mycls, keys=None):
            if keys:
                keys = map(str, keys)
                return [v for k, v in mycls._INSTANCES.iteritems() if k in keys]

            return mycls._INSTANCES.values()

        @classmethod
        @contextmanager
        def raise_on_duplicate(mycls):
            (
                sentinel,
                mycls.raise_on_duplicate_enabled,
            ) = (
                mycls.raise_on_duplicate_enabled,
                True,
            )

            try:
                yield
            finally:
                mycls.raise_on_duplicate_enabled = sentinel

        attrs.setdefault('memoization_key', cls.DEFAULT_MEMOIZATION_KEY)
        attrs.setdefault('propagate_memoization_key', cls.DEFAULT_PROPAGATE_MEMOIZATION_KEY)
        attrs['_INSTANCES'] = {}
        attrs['get_instance'] = get_instance
        attrs['get_instances'] = get_instances
        attrs.setdefault('__str__', lambda self: getattr(self, self.memoization_key))
        attrs['raise_on_duplicate'] = raise_on_duplicate
        attrs['raise_on_duplicate_enabled'] = True

        return super(Memoized, cls).__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        if cls.propagate_memoization_key:
            if cls.memoization_key in kwargs:
                key = kwargs[cls.memoization_key]
            else:
                key = args[0]
        else:
            if cls.memoization_key in kwargs:
                key = kwargs.pop(cls.memoization_key)
            else:
                key = args[0]
                args = args[1:]

        if key not in cls._INSTANCES:
            cls._INSTANCES[key] = super(Memoized, cls).__call__(*args, **kwargs)
            setattr(cls._INSTANCES[key], cls.memoization_key, key)
        elif cls.raise_on_duplicate_enabled:
            raise TeapotError("An instance of %s with the name '%s' already exists.", hl(cls.__name__), hl(key))

        return cls._INSTANCES[key]


class MemoizedObject(object):
    """
    A memoized base class.
    """

    __metaclass__ = Memoized
