"""
Contains all tea-party builders logic.
"""

from tea_party.filters import Filtered


def make_builders(attendee, builders):
    """
    Make a list of builders from a dictionary.
    """

    if not builders:
        return []

    return [make_builder(attendee, name, attributes) for name, attributes in builders.items()]

def make_builder(attendee, name, attributes):
    """
    Make a builder from its attributes.
    """

    if not attributes:
        attributes = {}

    tags = attributes.get('tags')

    if not tags:
        tags = []
    elif isinstance(tags, basestring):
        tags = [tags]

    command = attributes.get('command')

    if not command:
        command = None
    elif isinstance(command, basestring):
        command = [command]

    script = attributes.get('script')

    if not script:
        script = None

    filters = attributes.get('filters')

    return Builder(
        attendee=attendee,
        name=name,
        tags=tags,
        command=command,
        script=script,
        filters=filters,
        directory=attributes.get('directory'),
    )


class Builder(Filtered):

    """
    A Builder represents a way to build an attendee.
    """

    def __init__(self, attendee, name, tags, command=None, script=None, filters=[], directory=None):
        """
        Initialize a builder attached to `attendee` with the specified `name`.

        A builder may have `tags`, which must be a list of strings.

        You may specify either `command`, a list of commands to call for the
        build to take place, or `script`, an executable file to launch that
        will build everything.

        Specifying both will raise a ValueError.

        `filters` is a list of filters that must all validate in order for the
        build to be active in the current environment.

        `directory`, if specified, is a directory relative to the source root,
        where to go before issuing the build command or calling the build
        script.
        """

        if command and script:
            raise ValueError('You may only specify only one of `command` or `script`.')

        self.attendee = attendee
        self.name = name
        self.tags = tags
        self.command = command or None
        self.script = script or None
        self.directory = directory or None

        Filtered.__init__(self, filters=filters)

    def __str__(self):
        """
        Get the name of the builder.
        """

        return self.name

    def __repr__(self):
        """
        Get a representation of the builder.
        """

        return '<%s.%s(name=%r, tags=%r, command=%r, script=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.name,
            self.tags,
            self.command,
            self.script,
        )
