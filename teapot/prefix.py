"""
A prefix class.
"""

import os


class PrefixedObject(object):

    """
    A class that has a prefix member.
    """

    def __init__(self, prefix=None, *args, **kwargs):
        super(PrefixedObject, self).__init__(*args, **kwargs)
        self._prefix = prefix

    @property
    def prefix(self):
        return self._prefix or ''

    @prefix.setter
    def prefix(self, value):
        self._prefix = value
