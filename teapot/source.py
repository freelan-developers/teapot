"""
A source class.
"""

from .filters import FilteredObject
from .fetchers import Fetcher


class Source(FilteredObject):

    """
    Represents a project to build.
    """

    def __init__(self, resource, mimetype=None, fetcher=None, *args, **kwargs):
        """
        Create a source that maps on the specified resource.
        """

        super(Source, self).__init__(*args, **kwargs)

        self.resource = resource
        self._mimetype = mimetype
        self._fetcher = fetcher

    def __str__(self):
        """
        Get a string representation of the source.
        """

        return self.resource

    @property
    def fetcher(self):
        if not self._fetcher:
            return Fetcher.get_instance_for(source=self)

        if isinstance(self._fetcher, basestring):
            return Fetcher.get_instance_or_fail(name=self._fetcher)

        return self._fetcher
