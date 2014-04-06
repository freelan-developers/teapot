"""
The filters.
"""

from .builtin import *

from ..error import TeapotError
from ..log import Highlight as hl
from .filter import Filter, f_


class FilteredObject(object):
    """
    Inherit from this class when your object can be disabled by filters.
    """

    def __init__(self, filter=None):
        self._filter = filter

    @classmethod
    def get_enabled_instances(cls, keys=None):
        return [x for x in cls.get_instances(keys=keys) if x.enabled]

    @property
    def filter(self):
        if isinstance(self._filter, basestring):
            return Filter.get_instance_or_fail(self._filter)

        return self._filter

    def set_filter(self, filter):
        """
        Set the `filter` to check.

        `filter` can be None, a string, or a Filter instance.
        """

        self._filter = filter

        return self

    @property
    def enabled(self):
        """
        Check if the instance is filtered out.
        """

        return self.filter if self.filter is not None else True
