"""
A Memoized metaclass.
"""

import functools


class Memoized(type):

    """
    A Memoized type.
    """

    DEFAULT_MEMOIZATION_KEY = 'name'

    def __new__(cls, name, bases, attrs):

        @classmethod
        def get_instances(mycls):
            return mycls._INSTANCES.values()

        attrs.setdefault('memoization_key', cls.DEFAULT_MEMOIZATION_KEY)
        attrs['_INSTANCES'] = {}
        attrs['get_instances'] = get_instances
        attrs['__str__'] = lambda self: getattr(self, self.memoization_key)

        return super(Memoized, cls).__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        if cls.memoization_key in kwargs:
            key = kwargs.pop(cls.memoization_key)
        else:
            key = args[0]

        if key not in cls._INSTANCES:
            cls._INSTANCES[key] = super(Memoized, cls).__call__(*args[1:], **kwargs)
            setattr(cls._INSTANCES[key], cls.memoization_key, key)

        return cls._INSTANCES[key]


class MemoizedObject(object):
    """
    A memoized base class.
    """

    __metaclass__ = Memoized
