"""
Contains all tea-party builders logic.
"""

from tea_party.builders.filters import get_filter_by_name


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

    command = attributes.get('command')

    if not command:
        command = None
    elif isinstance(command, basestring):
        command = [command]
    else:
        command = command

    script = attributes.get('script')

    if not script:
        script = None

    filters = attributes.get('filters')

    if not filters:
        filters = []
    elif isinstance(filters, basestring):
        filters = [get_filter_by_name(filters)]
    else:
        filters = map(get_filter_by_name, filters)

    return Builder(
        attendee=attendee,
        name=name,
        command=command,
        script=script,
        filters=filters,
        directory=attributes.get('directory'),
    )


class Builder(object):

    """
    A Builder represents a way to build an attendee.
    """

    def __init__(self, attendee, name, command=None, script=None, filters=[], directory=None):
        """
        Initialize a builder attached to `attendee` with the specified `name`.

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
        self.command = command or None
        self.script = script or None
        self.filters = filters
        self.directory = directory or None
