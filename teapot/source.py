"""
A source class.
"""

from .filters import FilteredObject


class Source(FilteredObject):

    """
    Represents a project to build.
    """

    def __init__(self, resource, *args, **kwargs):
        """
        Create a source that maps on the specified resource.
        """

        super(Source, self).__init__(*args, **kwargs)

        self.resource = resource

    def __str__(self):
        """
        Get a string representation of the source.
        """

        return self.resource
