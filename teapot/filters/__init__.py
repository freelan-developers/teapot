"""
The filters.
"""

from .builtin import *

from ..error import TeapotError
from ..log import Highlight as hl
from .filter import Filter


class FilteredObject(object):
    """
    Inherit from this class when your object can be disabled by filters.
    """

    def __init__(self):
        self._filter = None

    @classmethod
    def get_enabled_instances(cls, keys=None):
        return [x for x in cls.get_instances(keys=keys) if x.enabled]

    @property
    def filter(self):
        if isinstance(self._filter, basestring):
            f = Filter.get_instance(self._filter)

            if not f:
                raise TeapotError("Unable to find the filter %s.", hl(self._filter))

            return f

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

        return self.filter() if self.filter else True
