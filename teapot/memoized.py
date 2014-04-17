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

    def __new__(cls, name, bases, attrs):

        attrs.setdefault('public_name', name)
        attrs['_INSTANCES'] = {}

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

    memoization_key = 'name'
    propagate_memoization_key = False
    raise_on_duplicate_enabled = False
    no_such_instance_message = "No %s could be found that has the %s %s."
    no_such_instance_args = ('classname', 'keyname', 'key')

    class NoSuchInstance(TeapotError):

        """
        A non-existing instance was requested.
        """

        def __init__(self, cls, key):
            super(cls.NoSuchInstance, self).__init__(
                cls.get_no_such_instance_message(key),
                *cls.get_no_such_instance_args(key)
            )
            self.cls = cls
            self.key = key

    @classmethod
    def get_no_such_instance_message(cls, key):
        return cls.no_such_instance_message

    @classmethod
    def get_no_such_instance_args(cls, key):
        values = {
            'classname': hl(cls.public_name),
            'keyname': cls.memoization_key,
            'key': hl(key),
            'self': hl(self),
        }

        return map(values.get, cls.no_such_instance_args)

    @classmethod
    def get_instance(cls, key, default=None):
        return cls._INSTANCES.get(key, default)

    @classmethod
    def get_instance_or_fail(cls, key):
        instance = cls.get_instance(key)

        if instance is None:
            raise cls.NoSuchInstance(cls, key)

        return instance

    @classmethod
    def get_instances(cls, keys=None):
        if keys is not None:
            keys = [getattr(key, cls.memoization_key) if isinstance(key, cls) else key for key in keys]

            result = []

            for key in keys:
                if key not in cls._INSTANCES:
                    raise cls.NoSuchInstance(cls, key)
                result.append(cls._INSTANCES[key])

            return result

        return cls._INSTANCES.values()

    @classmethod
    @contextmanager
    def raise_on_duplicate(cls):
        (
            sentinel,
            cls.raise_on_duplicate_enabled,
        ) = (
            cls.raise_on_duplicate_enabled,
            True,
        )

        try:
            yield
        finally:
            cls.raise_on_duplicate_enabled = sentinel

    @classmethod
    def clear_instances(cls, keys=None):
        if keys:
            keys = [getattr(key, cls.memoization_key) if isinstance(key, cls) else key for key in keys]

            for key in keys:
                if key in cls._INSTANCES:
                    del cls._INSTANCES[key]
        else:
            cls._INSTANCES = {}

    def __str__(self):
        return getattr(self, self.memoization_key)

    def __hash__(self):
        return hash(getattr(self, self.memoization_key))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and getattr(other, other.memoization_key) == getattr(self, self.memoization_key)
