"""
Contains all tea-party builders logic.
"""

import os
import re
import math
import signal
import subprocess

from contextlib import contextmanager
from threading import Thread

from tea_party.log import LOGGER, print_normal, print_error
from tea_party.log import Highlight as hl
from tea_party.filters import Filtered
from tea_party.environments import make_environment
from tea_party.extensions import parse_extension


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

    environment = attributes.get('environment')

    if environment:
        if isinstance(environment, basestring):
            environment = attendee.party.get_environment_by_name(environment)
        else:
            environment = make_environment(attendee.party, '%s:<unnamed environment>' % attendee.name, environment)
    else:
        environment = make_environment(attendee.party, '%s:<unnamed environment>' % attendee.name, {})

    return Builder(
        attendee=attendee,
        name=name,
        tags=tags,
        commands=commands,
        environment=environment,
        filters=filters,
        directory=attributes.get('directory'),
        prefix=prefix,
    )


class Builder(Filtered):

    """
    A Builder represents a way to build an attendee.
    """

    def __init__(self, attendee, name, tags, commands, environment, filters=[], directory=None, prefix=None):
        """
        Initialize a builder attached to `attendee` with the specified `name`.

        A builder may have `tags`, which must be a list of strings.

        You must specify `commands`, a list of commands to call for the build to
        take place.

        `environment` is the environment to use for the build.

        `filters` is a list of filters that must all validate in order for the
        build to be active in the current environment.

        `directory`, if specified, is a directory relative to the source root,
        where to go before issuing the build commands.

        `prefix` is a prefix that will be added to the right of the global
        prefix inside the $PREFIX variable.
        """

        if not commands:
            raise ValueError('A builder must have at least one command.')

        assert environment

        self.attendee = attendee
        self.name = name
        self.tags = tags
        self.commands = commands or []
        self.environment = environment
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

    @contextmanager
    def chdir(self, path):
        """
        Change the current directory.
        """

        old_path = os.getcwd()

        LOGGER.debug('Moving to: %s', hl(path))
        os.chdir(path)

        try:
            yield path
        finally:
            LOGGER.debug('Moving back to: %s', hl(old_path))
            os.chdir(old_path)

    def build(self, build_directory, verbose=False):
        """
        Build the attendee.
        """

        if self.directory:
            source_tree_path = os.path.join(build_directory, self.directory)
        else:
            source_tree_path = build_directory

        with self.chdir(source_tree_path):
            os.chdir(source_tree_path)

            with self.environment.enable() as env:
                for key, value in os.environ.iteritems():
                    LOGGER.debug('%s: %s', key, hl(value))

                for index, command in enumerate(self.commands):
                    command = self.apply_extensions(command)
                    LOGGER.important('%s: %s', ('%%0%sd' % int(math.ceil(math.log10(len(self.commands))))) % index, command)

                    if env:
                        process = subprocess.Popen(env.shell + [command], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    def handler(signum, frame):
                        LOGGER.warning('The building process was interrupted by the user.')
                        process.terminate()

                    previous_handler = signal.signal(signal.SIGINT, handler)

                    try:
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

                    finally:
                        signal.signal(signal.SIGINT, previous_handler)

                    if process.returncode != 0:
                        if not verbose:
                            for func, line in mixed_output:
                                func(line)

                        raise subprocess.CalledProcessError(returncode=process.returncode, cmd=command)

    def apply_extensions(self, command):
        """
        Apply the extensions to the command.
        """

        def replace(match):
            code = match.group('code')

            return parse_extension(code, self)

        return re.sub(r'\{{(?P<code>[\w\s()]+)}}', replace, command)
