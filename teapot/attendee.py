"""
An attendee class.
"""

from .memoized import MemoizedObject

from .error import TeapotError
from .source import Source
from .log import LOGGER, Highlight as hl
from .filters import FilteredObject


class Attendee(MemoizedObject, FilteredObject):

    """
    Represents a project to build.
    """

    propagate_memoization_key = True

    def __init__(self, name):
        self._depends_on = []
        self.sources = []

        super(Attendee, self).__init__()

    def __repr__(self):
        """
        Get a representation of the attendee.
        """

        return 'Attendee(%r)' % self.name

    def depends_on(self, *attendees):
        """
        Make the attendee depend on one or several other attendees.

        `attendees` is a list of attendees to depend on.
        """

        self._depends_on.extend(attendees)
        return self

    def add_source(self, resource, *args, **kwargs):
        """
        Add a source to the attendee.

        `resource` is the resource to add to the attendee.
        """

        if not isinstance(resource, Source):
            resource = Source(resource, *args, **kwargs)

        self.sources.append(resource)
        return self

    def fetch(self):
        """
        Fetch the most appropriate source.
        """

        LOGGER.info('Fetching %s...', hl(self))

        if not self.sources:
            raise TeapotError("No source specified for the attendee %s.", hl(self))
