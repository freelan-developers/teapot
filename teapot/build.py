"""
A build class.
"""

from .memoized import MemoizedObject
from .error import TeapotError
from .log import LOGGER, Highlight as hl
from .filters import FilteredObject
from .environment import Environment


class Build(MemoizedObject, FilteredObject):

    """
    Represents a build.
    """

    memoization_keys = ('attendee', 'name')
    propagate_memoization_keys = True

    @classmethod
    def transform_memoization_keys(cls, attendee, name):
        """
        Make sure the attendee parameter is a real Attendee instance.
        """

        if isinstance(attendee, basestring):
            from .attendee import Attendee

            attendee = Attendee(attendee)

        return attendee, name

    def __init__(self, attendee, name, environment=None, *args, **kwargs):
        super(Build, self).__init__(*args, **kwargs)
        self._environment = environment

        # Register the build in the Attendee.
        self.attendee = attendee
        self.name = name
        attendee.add_build(self)

    @property
    def environment(self):
        return Environment(self._environment)

    def __repr__(self):
        """
        Get a representation of the build.
        """

        return 'Build(%r, %r)' % (self.attendee, self.name)

    def __str__(self):
        """
        Get a string representation of the build.
        """

        return '%s_%s' % (self.attendee, self.name)
