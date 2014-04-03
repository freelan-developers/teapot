"""
A Memoized metaclass.
"""

import functools


class Memoized(type):

    """
    A Memoized type.
    """

    def __new__(cls, name, bases, attrs):
        def __new__(cls, name, *args, **kwargs):
            if not name in cls.MEMOIZED_INSTANCES:
                cls.MEMOIZED_INSTANCES[name] = object.__new__(cls, *args, **kwargs)

            return cls.MEMOIZED_INSTANCES[name]

        @classmethod
        def get_instances(cls):
            """
            Get all the existing instances.
            """

            return cls.MEMOIZED_INSTANCES.values()

        attrs['MEMOIZED_INSTANCES'] = {}
        attrs['__new__'] = __new__
        attrs['get_instances'] = get_instances
        return type.__new__(cls, name, bases, attrs)


class MemoizedObject(object):
    """
    A memoized base class.
    """

    __metaclass__ = Memoized
