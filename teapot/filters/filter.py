"""
A base filter class.
"""

from functools import wraps

from ..memoized import MemoizedObject


class UnamedFilter(object):
    """
    A generic filter class.
    """

    def __init__(self, condition=None):
        self.condition = condition

    def __call__(self, *args, **kwargs):
        if self.condition:
            try:
                return self.condition(*args, **kwargs)
            except:
                return self.condition

        return False


class Filter(MemoizedObject, UnamedFilter):
    pass


class named_filter(object):

    """
    A filter-maker decorator.
    """

    def __init__(self, name, depends_on=None):

        if isinstance(depends_on, basestring):
            depends_on = [depends_on]

        self.name = name
        self.depends_on = depends_on

    def __call__(self, func):
        if self.depends_on:
            @wraps(func)
            def depends_on_func(*args, **kwargs):
                for dep in self.depends_on:
                    if isinstance(dep, basestring):
                        dep = Filter.get_instance(dep)

                    if not dep(*args, **kwargs):
                        return False

                return func(*args, **kwargs)

            condition = depends_on_func
        else:
            condition = func

        Filter(name=self.name, condition=condition)
        return func
