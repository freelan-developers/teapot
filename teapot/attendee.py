"""
An attendee class.
"""

from .memoized import MemoizedObject


class Attendee(MemoizedObject):

    """
    Represents a project to build.
    """

    def ___repr__(self):
        """
        Get a representation of the attendee.
        """

        return 'Attendee(%r)' % self.name

    def depends(self, attendees):
        """
        Make the attendee depend on one or several other attendees.
        """
