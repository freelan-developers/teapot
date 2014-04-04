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

    def __call__(self, *args, **kwargs):
        if self._condition:
            try:
                return self._condition(*args, **kwargs)
            except:
                return self._condition

        return False


class Filter(MemoizedObject, UnamedFilter):
    pass


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
            def depends_on_func(*args, **kwargs):
                if isinstance(self.depends_on, basestring):
                    depends_on_filter = Filter.get_instance(self.depends_on)

                    if not depends_on_filter:
                        raise TeapotError("Unable to find the filter named %s.", hl(self.depends_on))

                    if not depends_on_filter(*args, **kwargs):
                        return False
                else:
                    if not self.depends_on(*args, **kwargs):
                        return False

                return func(*args, **kwargs)

            condition = depends_on_func
        else:
            condition = func

        Filter(name=self.name, condition=condition)
        return func
