"""
Contains all tea-party builders logic.
"""

import os
import sys
import math
import subprocess

from tea_party.log import LOGGER
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

    commands = attributes.get('commands', [])

    if isinstance(commands, basestring):
        commands = [commands]

    filters = attributes.get('filters')

    return Builder(
        attendee=attendee,
        name=name,
        tags=tags,
        commands=commands,
        filters=filters,
        directory=attributes.get('directory'),
    )


class Builder(Filtered):

    """
    A Builder represents a way to build an attendee.
    """

    def __init__(self, attendee, name, tags, commands, filters=[], directory=None):
        """
        Initialize a builder attached to `attendee` with the specified `name`.

        A builder may have `tags`, which must be a list of strings.

        You must specify `commands`, a list of commands to call for the build to
        take place.

        `filters` is a list of filters that must all validate in order for the
        build to be active in the current environment.

        `directory`, if specified, is a directory relative to the source root,
        where to go before issuing the build commands.
        """

        if not commands:
            raise ValueError('A builder must have at least one command.')

        self.attendee = attendee
        self.name = name
        self.tags = tags
        self.commands = commands or []
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

        return '<%s.%s(name=%r, tags=%r, commands=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.name,
            self.tags,
            self.commands,
        )

    def build(self, verbose=False):
        """
        Build the attendee.
        """

        current_dir = os.getcwd()

        try:
            if self.directory:
                source_tree_path = os.path.join(self.attendee.source_tree_path, self.directory)
            else:
                source_tree_path = self.attendee.source_tree_path

            os.chdir(source_tree_path)

            for index, command in enumerate(self.commands):
                LOGGER.important('%s: %s', ('%%0%sd' % int(math.ceil(math.log10(len(self.commands))))) % index, command)

                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                output = ''

                for line in iter(process.stdout.readline, ''):
                    output += line

                    if verbose:
                        sys.stdout.write(line)

                process.wait()

                if process.returncode != 0:
                    if not verbose:
                        sys.stderr.write(output)

                    raise subprocess.CalledProcessError(returncode=process.returncode, cmd=command)
        finally:
            os.chdir(current_dir)
