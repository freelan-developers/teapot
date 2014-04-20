"""
An environment class.
"""

import os
import re
import sys

from contextlib import contextmanager

from .memoized import MemoizedObject
from .error import TeapotError
from .log import LOGGER, Highlight as hl
from .signature import SignableObject


class Environment(MemoizedObject, SignableObject):

    """
    Represents a build environment.
    """

    propagate_memoization_keys = True
    signature_fields = ('variables', 'shell', 'parent')

    @staticmethod
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

    def __init__(self, name, variables=None, shell=None, parent=None, *args, **kwargs):
        """
        Create a new environment.

        `variables` is a dictionary of environment variables to use.

        `shell`, if specified, is the path to a shell to use, or parts of a
        shell to use. Variables in `shell` will be substitued using the parent
        environment, if any. If `shell` is True, then the shell from the parent
        environment will be used.

        `parent` is an Environment instance or the name of an Environment
        instance to inherit from. If `parent` is None, the environment will
        be blank.
        """

        self._parent = parent
        self.variables = variables or {}
        self._shell = shell

        super(Environment, self).__init__(*args, **kwargs)

    def __repr__(self):
        """
        Get a representation of the environment.
        """

        return 'Environment(%r)' % self.name

    def depends_on(self, environment):
        """
        Make the environment depend on one other environment.

        `environment` is either a string or an Environment instance.
        """

        self._parent = environment
        return self

    @property
    def parent(self):
        """
        Get the parent environment, if any.
        """

        if isinstance(self._parent, basestring):
            self._parent = self.get_instance_or_fail(self._parent)
        elif isinstance(self._parent, Environment):
            pass
        elif self._parent is not None:
            raise TeapotError(
                "An invalid parent %s was specified for environment %s.",
                hl(repr(self._parent)),
                hl(self),
            )

        return self._parent

    @property
    def children(self):
        """
        Get environments that directly depend on this environment.
        """

        return {
            environment for environment in self.get_instances()
            if self == environment.parent
        }

    @property
    def shell(self):
        if self._shell is True:
            shell = self.parent._shell if self.parent else None
        elif isinstance(self._shell, basestring):
            shell = [self._shell]
        else:
            shell = self._shell

        if shell:
            if self.parent:
                with self.parent.enable():
                    return map(lambda arg: self.perform_substitutions(arg, os.environ), shell)
            else:
                return map(lambda arg: self.perform_substitutions(arg, {}), shell)

    @shell.setter
    def shell(self, value):
        self._shell = value

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
            if self.parent:
                with self.parent.enable(silent=True):
                    if not silent:
                        LOGGER.info('Entering environment %s...', hl(self))

                    for key, value in self.variables.iteritems():
                        if value is not None:
                            os.environ[key] = self.perform_substitutions(value, saved_environ)
                        else:
                            if key in os.environ:
                                del os.environ[key]

                    yield self
            else:
                if not silent:
                    LOGGER.info('Entering environment %s...', hl(self))

                os.environ.clear()

                for key, value in self.variables.iteritems():
                    if value is not None:
                        os.environ[key] = self.perform_substitutions(value, saved_environ)
                    else:
                        if key in saved_environ:
                            os.environ[key] = saved_environ.get(key)

                yield self

        finally:
            if not silent:
                LOGGER.info('Exiting environment %s...', hl(self))

            os.environ.clear()
            os.environ.update(saved_environ)


# Create the empty and system environments.
Environment('empty')
Environment('system', variables=os.environ.copy())
