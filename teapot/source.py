"""
A source class.
"""

from .filters import FilteredObject
from .fetchers import Fetcher
from .memoized import MemoizedObject


class Source(MemoizedObject, FilteredObject):

    """
    Represents a project to build.
    """

    memoization_keys = ('attendee', 'resource')
    propagate_memoization_keys = True

    @classmethod
    def transform_memoization_keys(cls, attendee, resource):
        """
        Make sure the attendee parameter is a real Attendee instance.
        """

        if isinstance(attendee, basestring):
            from .attendee import Attendee

            attendee = Attendee(attendee)

        return attendee, resource

    def __init__(self, attendee, resource, mimetype=None, fetcher=None, *args, **kwargs):
        """
        Create a source that maps on the specified resource.
        """
        super(Source, self).__init__(*args, **kwargs)

        self.mimetype = mimetype
        self._fetcher = fetcher
        self._parsed_source = None

        # Register the source in the Attendee.
        self.attendee = attendee
        self.resource = resource
        attendee.add_source(self)

    def __str__(self):
        """
        Get a string representation of the source.
        """

        return self.resource

    @property
    def fetcher(self):
        if not self._fetcher:
            self._fetcher = Fetcher.get_instance_for(source=self)

        if isinstance(self._fetcher, basestring):
            self._fetcher = Fetcher.get_instance_or_fail(name=self._fetcher)

        return self._fetcher

    @property
    def parsed_source(self):
        if self._parsed_source is None:
            self._parsed_source = self.fetcher.parse_source(source=self)

        return self._parsed_source

    def fetch(self, target_path):
        """
        Fetches the source.
        """

        return self.fetcher.fetch(
            parsed_source=self.parsed_source,
            target_path=target_path,
        )
