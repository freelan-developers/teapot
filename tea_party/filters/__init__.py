"""
The filters.
"""

from tea_party.filters.builtin import *
from tea_party.filters.decorators import get_filter_by_name


class Filtered(object):
    """
    Inherit from this class when your object can be disabled by filters.
    """

    def __init__(self, filters=[]):
        """
        Set the `filters` to check.

        `filters` can be None, a string, or a list of strings that will be
        resolved.
        """

        if not filters:
            self.filters = []
        elif isinstance(filters, basestring):
            self.filters = [get_filter_by_name(filters)]
        else:
            self.filters = map(get_filter_by_name, filters)

    @property
    def enabled(self):
        """
        Check if the instance is filtered out.
        """

        return all(f() for f in self.filters)
