"""
A base filter class.
"""

from functools import wraps

from ..memoized import MemoizedObject
from ..error import TeapotError
from ..log import Highlight as hl


class UnamedFilter(object):
    """
    A generic filter class.
    """

    def __init__(self, condition=None):
        self._condition = condition

    def __nonzero__(self):
        if self._condition:
            try:
                return bool(self._condition())
            except TypeError:
                if isinstance(self._condition, basestring):
                    return bool(Filter.get_instance_or_fail(self._condition))

                return bool(self._condition)

        return False

    def __and__(self, other):
        return UnamedFilter(condition=lambda: self and other)

    def __or__(self, other):
        return UnamedFilter(condition=lambda: self or other)

    def __invert__(self):
        return UnamedFilter(condition=lambda: not self)

    def __xor__(self, other):
        return UnamedFilter(condition=lambda: (self or other) and not (self and other))


class Filter(MemoizedObject, UnamedFilter):

    propagate_memoization_keys = True
    no_such_instance_message = "No filter named %s could be found. Did you mistype the filter's name ?"
    no_such_instance_args = ('key_name',)

    def __init__(self, name, condition=None):
        if condition is None:
            raise TeapotError(
                (
                    "A filter definition for %s must contain a non-None "
                    "condition. Did you mistype the filter's name ?"
                ),
                hl(name),
            )

        super(Filter, self).__init__(condition=condition)


class named_filter(object):

    """
    A filter-maker decorator.
    """

    def __init__(self, name, depends_on=None):
        """
        Define a named filter from a function.

        `name` is the name of the filter to create. If a filter with
        that name already exists, a TeapotError is raised.

        `depends_on` is another filter to depend on. It can be either a
        filter instance or the name of a named filter.
        """

        self.name = name
        self.depends_on = depends_on

    def __call__(self, func):
        if self.depends_on:
            @wraps(func)
            def depends_on_condition():
                if isinstance(self.depends_on, basestring):
                    depends_on_filter = Filter.get_instance_or_fail(self.depends_on)

                    if not depends_on_filter:
                        return False
                else:
                    if not self.depends_on:
                        return False

                return func()

            condition = depends_on_condition
        else:
            condition = func

        with Filter.raise_on_duplicate():
            Filter(name=self.name, condition=condition)

        return func


uf = UnamedFilter
f = Filter
