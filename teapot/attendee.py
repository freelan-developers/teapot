"""
An attendee class.
"""

from .memoized import MemoizedObject


class Attendee(MemoizedObject):

    """
    Represents a project to build.
    """

    def __init__(self, name):
        """
        Initializes the attendee.

        `name` is the name of the attendee.
        """
        self.name = name

    def __str__(self):
        """
        Get a string representation of the attendee.
        """

        return self.name

    def ___repr__(self):
        """
        Get a representation of the attendee.
        """

        return 'Attendee(%r)' % self.name
