"""
An attendee class.
"""

from .memoized import MemoizedObject
from .filters import FilteredObject
from .error import TeapotError
from .source import Source
from .log import LOGGER, Highlight as hl


class Attendee(MemoizedObject, FilteredObject):

    """
    Represents a project to build.
    """

    propagate_memoization_key = True

    def __init__(self, name, *args, **kwargs):
        self._depends_on = []
        self._sources = []

        super(Attendee, self).__init__(*args, **kwargs)

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

    @property
    def sources(self):
        """
        Get all the active sources.
        """

        return [x for x in self._sources if x.enabled]

    def add_source(self, resource, *args, **kwargs):
        """
        Add a source to the attendee.

        `resource` is the resource to add to the attendee.
        """

        if not isinstance(resource, Source):
            resource = Source(resource, *args, **kwargs)

        self._sources.append(resource)
        return self

    def fetch(self):
        """
        Fetch the most appropriate source.
        """

        LOGGER.info('Fetching %s...', hl(self))

        if not self.sources:
            raise TeapotError(
                (
                    "No enabled source was found for the attendee %s. "
                    "Did you forget to set a filter on the attendee ?"
                ),
                hl(self),
            )
