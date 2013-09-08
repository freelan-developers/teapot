"""
Tea-party environments.
"""

import os
import shlex

from contextlib import contextmanager

from tea_party.log import LOGGER
from tea_party.log import Highlight as hl


DEFAULT_ENVIRONMENT_NAME = 'default'

def make_environments(party, environments):
    """
    Make a list of environments from a dictionary.

    If `environments` is a dictionary, make_environment() is called on every
    element, and the result is appended the returned value.

    If `environments` is falsy, an empty list is returned.
    """

    if environments:
        return [
            make_environment(party, name, environment)
            for name, environment
            in environments.items()
        ]

    return []

def make_environment(party, name, environment):
    """
    Make an environment from a dictionary of its attributes.

    `party` is the Party instance to link to.

    `name`, is the name of the environment. If `name` is equal to
    DEFAULT_ENVIRONMENT_NAME, a ValueError is raised.

    `environment` is a dictionary of attributes.
    """

    if name == DEFAULT_ENVIRONMENT_NAME:
        raise ValueError('Cannot create an environment with name "%s": it is reserved for the default environment.' % name)

    shell = environment.get('shell')

    if shell is not None:
        if isinstance(shell, basestring):
            shell = shlex.split(shell)

    inherit = environment.get('inherit')

    if inherit:
        if isinstance(inherit, basestring):
            inherit = party.get_environment_by_name(inherit)
        else:
            inherit = make_environment(party, name + ':<unnamed base environment>', inherit)

    return Environment(
        party=party,
        name=name,
        variables=environment.get('variables', {}),
        inherit=inherit,
        shell=shell,
    )

class Environment(object):

    """
    Represents an environment for builders.
    """

    @staticmethod
    def get_default(party):
        """
        Get the default environment.
        """

        return Environment(
            party=party,
            name=DEFAULT_ENVIRONMENT_NAME,
            variables=os.environ.copy(),
            inherit=None,
            shell=None,
        )

    def __init__(self, party, name, variables=None, inherit=None, shell=None):
        """
        Initialize a new Environment.

        `party` is the party instance to which the environment belongs.

        `name`, is the name of the environment.

        `variables`, if specified, is a map of the variables and their values.

        `inherit` is the environment to inherit from, or None, if an empty base
        environment is preferred.

        `shell`, if specified, is the shell to use to execute the commands
        during builds.
        """

        self.party = party
        self.name = name
        self.variables = variables or {}
        self.inherit = inherit
        self.shell = shell

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
    def enable(self):
        """
        Enable the environment and shell settings, if any.

        The current process environment is modified during the call, and
        restored when the function returns.

        set_shell() is supposed to be used with a `with` statement.
        """

        saved_environ = os.environ.copy()

        LOGGER.debug('Entering environment %s...', hl(self))

        try:
            def print_environment():
                """
                Print the current environment.
                """

                for key, value in os.environ.iteritems():
                    LOGGER.debug('%s: %s', key, hl(value))

            if self.inherit:
                LOGGER.debug('Inheriting environment from %s...', hl(self.inherit))

                with self.inherit.enable():
                    for key, value in self.variables.iteritems():
                        if value is not None:
                            os.environ[key] = value
                        else:
                            if key in os.environ:
                                del os.environ[key]

                    print_environment()

                    yield self
            else:
                LOGGER.debug('%s inheriting parent environment...', hl('Not'))

                os.environ.clear()

                for key, value in self.variables.iteritems():
                    if value is not None:
                        os.environ[key] = value
                    else:
                        if key in saved_environ:
                            os.environ[key] = saved_environ.get(key)

                print_environment()

                yield self

        finally:
            LOGGER.debug('Exiting environment %s...', hl(self))

            os.environ.clear()
            os.environ.update(saved_environ)
