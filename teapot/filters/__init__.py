"""
The filters.
"""

from ..error import TeapotError
from ..log import Highlight as hl
from .filter import Filter, f, uf


class FilteredObject(object):
    """
    Inherit from this class when your object can be disabled by filters.
    """

    def __init__(self, filter=None, *args, **kwargs):
        super(FilteredObject, self).__init__(*args, **kwargs)
        self._filter = filter

    @classmethod
    def get_enabled_instances(cls, keys_list=None, instances=None):
        if instances is None:
            instances = cls.get_instances(keys_list=keys_list)

        return [x for x in instances if x.enabled]

    @property
    def filter(self):
        if isinstance(self._filter, basestring):
            return Filter.get_instance_or_fail(self._filter)

        return self._filter

    @filter.setter
    def filter(self, filter):
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
