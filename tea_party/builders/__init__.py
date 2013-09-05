"""
Contains all tea-party builders logic.
"""

import os
import re
import math
import subprocess

from tea_party.log import LOGGER, print_normal, print_error
from tea_party.filters import Filtered
from threading import Thread


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
    prefix = attributes.get('prefix')

    return Builder(
        attendee=attendee,
        name=name,
        tags=tags,
        commands=commands,
        filters=filters,
        directory=attributes.get('directory'),
        prefix=prefix,
    )


class Builder(Filtered):

    """
    A Builder represents a way to build an attendee.
    """

    def __init__(self, attendee, name, tags, commands, filters=[], directory=None, prefix=None):
        """
        Initialize a builder attached to `attendee` with the specified `name`.

        A builder may have `tags`, which must be a list of strings.

        You must specify `commands`, a list of commands to call for the build to
        take place.

        `filters` is a list of filters that must all validate in order for the
        build to be active in the current environment.

        `directory`, if specified, is a directory relative to the source root,
        where to go before issuing the build commands.

        `prefix` is a prefix that will be added to the right of the global
        prefix inside the $PREFIX variable.
        """

        if not commands:
            raise ValueError('A builder must have at least one command.')

        self.attendee = attendee
        self.name = name
        self.tags = tags
        self.commands = commands or []
        self.directory = directory or None
        self.prefix = prefix or ''

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
                command = self.apply_extensions(command)
                command = self.replace_variables(command)
                LOGGER.important('%s: %s', ('%%0%sd' % int(math.ceil(math.log10(len(self.commands))))) % index, command)

                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                mixed_output = []

                def read_stdout():
                    for line in iter(process.stdout.readline, ''):
                        mixed_output.append((print_normal, line))

                        if verbose:
                            print_normal(line)

                def read_stderr():
                    for line in iter(process.stderr.readline, ''):
                        mixed_output.append((print_error, line))

                        if verbose:
                            print_error(line)

                stdout_thread = Thread(target=read_stdout)
                stdout_thread.daemon = True
                stdout_thread.start()

                stderr_thread = Thread(target=read_stderr)
                stderr_thread.daemon = True
                stderr_thread.start()

                stdout_thread.join()
                stderr_thread.join()

                process.wait()

                if process.returncode != 0:
                    if not verbose:
                        for func, line in mixed_output:
                            func(line)

                    raise subprocess.CalledProcessError(returncode=process.returncode, cmd=command)
        finally:
            os.chdir(current_dir)

    def apply_extensions(self, command):
        """
        Apply the extensions to the command.
        """

        #TODO: Support arguments for extensions

        extensions = {
            'attendee': self.attendee,
            'builder': self.name,
            'prefix': os.path.join(self.attendee.party.prefix, self.attendee.prefix, self.prefix),
            'attendee_prefix': os.path.join(self.attendee.party.prefix, self.attendee.prefix),
            'global_prefix': self.attendee.party.prefix,
        }

        def replace(match):
            key = next(value for value in match.groups() if value is not None)

            if not key in extensions:
                raise ValueError('Unknown extension {{%s}} in command "%s"' % (key, command))

            return str(extensions[key])

        return re.sub(r'\{{([a-zA-Z_]+)}}', replace, command)

    def replace_variables(self, command):
        """
        Replace the environment variables in the command.
        """

        def replace(match):
            key = next(value for value in match.groups() if value is not None)

            return os.environ.get(key)

        return re.sub(r'\$([a-zA-Z_]+)|\${([a-zA-Z_]+)}', replace, command)
