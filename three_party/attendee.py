"""
3party 'attendee' class.
"""

from three_party.source import make_sources


def make_attendees(data):
    """
    Build a list of attendees from an attendees data dictionary.
    """

    return [
        make_attendee(name, attributes)
        for name, attributes
        in data.items()
    ]


def make_attendee(name, attributes):
    """
    Create an attendee from a name a dictionary of attributes.
    """

    return Attendee(
        name=name,
        sources=make_sources(attributes.get('source')),
        depends=make_depends(attributes.get('depends')),
    )


def make_depends(depends):
    """
    Create a list of dependencies.

    `depends` can either be a single dependency name or a list of dependencies.

    If `depends` is False, an empty list is returned.
    """

    if not depends:
        return []

    elif isinstance(depends, basestring):
        return [depends]

    return depends


class Attendee(object):

    """
    An `Attendee` instance holds information about an attendee (third-party
    software).

    `sources` is a list of Source instances.
    `depends` is a list of Attendee names to depend on.
    """

    def __init__(self, name, sources, depends):
        """
        Create an attendee.
        """

        self.name = name
        self.sources = sources
        self.depends = depends

    def __repr__(self):
        """
        Get a representation of the source.
        """

        return '<%s.%s(name=%r, sources=%r, depends=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.name,
            self.sources,
            self.depends,
        )
