"""
A source class.
"""


class Source(object):

    """
    Represents a project to build.
    """

    def __init__(self, resource):
        """
        Create a source that maps on the specified resource.
        """

        self.resource = resource

    def __str__(self):
        """
        Get a string representation of the source.
        """

        return self.resource
