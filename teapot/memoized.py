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

    _ALL_INSTANCES = {}

    @classmethod
    def clear_all_instances(cls):
        for mcls in cls._ALL_INSTANCES.values():
            mcls.clear_instances()
            del mcls

        cls._ALL_INSTANCES = {}

    def __new__(cls, name, bases, attrs):

        attrs.setdefault('public_name', name)
        attrs['_INSTANCES'] = {}
        attrs['_INSTANCES_PARAMS'] = {}

        cls._ALL_INSTANCES[name] = super(Memoized, cls).__new__(cls, name, bases, attrs)
        return cls._ALL_INSTANCES[name]

    def __call__(cls, *args, **kwargs):
        keys, args, kwargs = cls.extract_keys_from_args(args, kwargs, remove_from_args=not cls.propagate_memoization_keys)
        keys = cls.transform_memoization_keys(*keys)

        if keys not in cls._INSTANCES:
            instance = super(Memoized, cls).__call__(*args, **kwargs)

            for memoization_key, key in zip(cls.memoization_keys, keys):
                setattr(instance, memoization_key, key)

            setattr(instance, 'keys', keys)

            cls._INSTANCES[keys] = instance
            cls._INSTANCES_PARAMS[keys] = (args, kwargs)

        elif cls.raise_on_duplicate_enabled:
            raise cls.DuplicateInstance(cls, keys)
        else:
            if cls.propagate_memoization_keys:
                keys, args, kwargs = cls.extract_keys_from_args(args, kwargs, remove_from_args=True)

            if (args or kwargs) and cls._INSTANCES_PARAMS[keys] != (args, kwargs):
                print (args, kwargs)
                print cls._INSTANCES_PARAMS[keys]
                raise cls.DuplicateInstance(cls, keys)

        return cls._INSTANCES[keys]


class MemoizedObject(object):
    """
    A memoized base class.
    """

    __metaclass__ = Memoized

    memoization_keys = ('name',)
    propagate_memoization_keys = False
    raise_on_duplicate_enabled = False
    duplicate_instance_message = "An instance of %s already exists with the keys %s."
    duplicate_instance_args = ('classname', 'keys')
    no_such_instance_message = "No %s could be found that matches the keys %s."
    no_such_instance_args = ('classname', 'keys')

    @classmethod
    def clear_instances(cls):
        cls._INSTANCES = {}
        cls._INSTANCES_PARAMS = {}

    @classmethod
    def transform_memoization_keys(cls, *args):
        return args

    class DuplicateInstance(TeapotError):

        """
        Another instance exist with those parameters.
        """

        def __init__(self, cls, keys):
            super(cls.DuplicateInstance, self).__init__(
                cls.get_duplicate_instance_message(keys),
                *cls.get_duplicate_instance_args(keys)
            )
            self.cls = cls
            self.keys = keys

    @classmethod
    def get_duplicate_instance_message(cls, keys):
        return cls.duplicate_instance_message

    @classmethod
    def get_duplicate_instance_args(cls, keys):
        values = {
            'classname': hl(cls.public_name),
            'keys': keys,
        }

        for memoization_key, key in zip(cls.memoization_keys, keys):
            values['key_%s' % memoization_key] = key

        return map(values.get, cls.duplicate_instance_args)

    class NoSuchInstance(TeapotError):

        """
        A non-existing instance was requested.
        """

        def __init__(self, cls, keys):
            super(cls.NoSuchInstance, self).__init__(
                cls.get_no_such_instance_message(keys),
                *cls.get_no_such_instance_args(keys)
            )
            self.cls = cls
            self.keys = keys

    @classmethod
    def get_no_such_instance_message(cls, keys):
        return cls.no_such_instance_message

    @classmethod
    def get_no_such_instance_args(cls, keys):
        values = {
            'classname': hl(cls.public_name),
            'keys': keys,
        }

        for memoization_key, key in zip(cls.memoization_keys, keys):
            values['key_%s' % memoization_key] = key

        return map(values.get, cls.no_such_instance_args)

    @classmethod
    def extract_keys_from_args(cls, args, kwargs, remove_from_args=True):
        """
        Get the keys from the specified arguments.

        If `remove_from_args` is true, then the extracted keys are
        removed from the returned `args` and `kwargs`.

        Return the keys, the `args` and the `kwargs`.
        """

        if (len(args) + len(kwargs)) < len(cls.memoization_keys):
            raise TypeError('Incorrect arguments. Got (%r, %r), expected %r' % (args, kwargs, cls.memoization_keys))

        args = list(args)
        kwargs = kwargs.copy()
        keys = []

        for index, arg in enumerate(args):
            memoization_key = cls.memoization_keys[index]

            if memoization_key in kwargs:
                raise TypeError('Got multiple values for keyword argument %r' % memoization_key)

            keys.append(arg)

        for memoization_key in cls.memoization_keys[len(args):]:
            if remove_from_args:
                keys.append(kwargs.pop(memoization_key))
            else:
                keys.append(kwargs[memoization_key])

        if remove_from_args:
            args = args[len(cls.memoization_keys):]

        return tuple(keys), tuple(args), kwargs

    @classmethod
    def get_instance(cls, *args, **kwargs):
        default = kwargs.pop('default', None)
        keys = cls.extract_keys_from_args(args, kwargs)[0]
        return cls._INSTANCES.get(keys, default)

    @classmethod
    def get_instance_or_fail(cls, *args, **kwargs):
        instance = cls.get_instance(*args, **kwargs)

        if instance is None:
            raise cls.NoSuchInstance(cls, keys=cls.extract_keys_from_args(args, kwargs)[0])

        return instance

    @classmethod
    def get_instances(cls, keys_list=None):
        if keys_list is not None:
            def to_keys(value):
                if isinstance(value, cls):
                    return value.keys

                if not isinstance(value, tuple):
                    return (value,)

                return value

            keys_list = map(to_keys, keys_list)

            result = []

            for keys in keys_list:
                if keys not in cls._INSTANCES:
                    raise cls.NoSuchInstance(cls, keys)
                result.append(cls._INSTANCES[keys])

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

    @property
    def memoization_str(self):
        return '-'.join(map(str, (getattr(self, memoization_key) for memoization_key in self.memoization_keys)))

    def __str__(self):
        return self.memoization_str

    def __hash__(self):
        return hash(self.memoization_str)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (other.memoization_str == self.memoization_str)
