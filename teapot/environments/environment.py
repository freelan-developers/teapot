"""
Teapot environment class.
"""

import os
import re
import sys
import json
import shlex
import hashlib

from contextlib import contextmanager

from teapot.log import LOGGER
from teapot.log import Highlight as hl


def perform_substitutions(value, parent_context):
    """
    Perform substitutions in the specified `value`.

    Values are taken from the `parent_context`. If no value is found in the
    parent context, the substitution is done with an empty string.

    Substitutions are done for $KEY on all platforms, and also for %KEY% on
    Windows.
    """

    if sys.platform.startswith('win32'):
        pattern = '\$(?P<unix_key>[A-Za-z_][A-Za-z_0-9]*)|%(?P<windows_key>[A-Za-z_][A-Za-z_0-9]*)%'
    else:
        pattern = '\$(?P<unix_key>[A-Za-z_][A-Za-z_0-9]*)'

    def substitute(match):
        key = match.group('unix_key') or match.group('windows_key')

        return parent_context.get(key, '')

    return re.sub(pattern, substitute, value)


class Environment(object):

    """
    Represents an environment for builders.
    """

    def __init__(self, name=None, variables=None, inherit=None, shell=None):
        """
        Initialize a new Environment.

        `name`, is the name of the environment.

        `variables`, if specified, is a map of the variables and their values.

        `inherit` is the environment to inherit from, or None, if an empty base
        environment is preferred.

        `shell`, if specified, is the shell to use to execute the commands
        during builds.

        `shell` may also be equal to True, in which case it will also inherit
        the shell from its inherited environment.
        """

        self.name = name or '<unnamed environment>'
        self.variables = variables or {}
        self.inherit = inherit
        self.shell = None

        if shell is True:
            if self.inherit:
                shell = self.inherit.shell
            else:
                shell = None

        if shell:
            if self.inherit:
                with self.inherit.enable(silent=True):
                    self.shell = map(lambda arg: perform_substitutions(arg, os.environ), shell)
            else:
                self.shell = map(lambda arg: perform_substitutions(arg, {}), shell)

    def __str__(self):
        """
        Get the name of the environment.
        """

        return self.name

    def __repr__(self):
        """
        Get a representation of the environment.
        """

        return '<%s.%s(name=%r, variables=%r, inherit=%r, shell=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.name,
            self.variables,
            self.inherit,
            self.shell,
        )

    @contextmanager
    def enable(self, silent=False):
        """
        Enable the environment and shell settings, if any.

        The current process environment is modified during the call, and
        restored when the function returns.

        If `silent` is truthy, no log output will be done.

        enable() is supposed to be used with a `with` statement.
        """

        saved_environ = os.environ.copy()

        try:
            if self.inherit:
                with self.inherit.enable(silent=True):
                    if not silent: LOGGER.info('Entering environment %s...', hl(self))

                    for key, value in self.variables.iteritems():
                        if value is not None:
                            os.environ[key] = perform_substitutions(value, saved_environ)
                        else:
                            if key in os.environ:
                                del os.environ[key]

                    yield self
            else:
                if not silent: LOGGER.info('Entering environment %s...', hl(self))

                os.environ.clear()

                for key, value in self.variables.iteritems():
                    if value is not None:
                        os.environ[key] = perform_substitutions(value, saved_environ)
                    else:
                        if key in saved_environ:
                            os.environ[key] = saved_environ.get(key)

                yield self

        finally:
            if not silent: LOGGER.info('Exiting environment %s...', hl(self))

            os.environ.clear()
            os.environ.update(saved_environ)

    @property
    def signature(self):
        """
        Get the signature of the environment.
        """

        data = {
            'name': self.name,
            'variables': self.variables,
            'inherit': self.inherit.signature if self.inherit else None,
            'shell': self.shell,
        }

        algorithm = hashlib.sha1()
        algorithm.update(json.dumps(data))

        result = algorithm.hexdigest()

        LOGGER.debug('%s\'s signature is: %s', hl(self), hl(result))

        return result
