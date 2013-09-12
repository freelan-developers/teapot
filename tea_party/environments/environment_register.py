"""
An environment register class.
"""

from tea_party.log import LOGGER
from tea_party.log import Highlight as hl


class NoSuchEnvironmentError(ValueError):

    """
    The specified environment does not exist.
    """

    def __init__(self, name):
        """
        Create an NoSuchEnvironmentError for the specified `name`.
        """

        super(NoSuchEnvironmentError, self).__init__(
            'No such environment: %s' % name
        )

        self.name = name


class EnvironmentAlreadyRegisteredError(ValueError):

    """
    An environment was already registered with that name.
    """

    def __init__(self, name):
        """
        Create an EnvironmentAlreadyRegisteredError for the specified ` name`.
        """

        super(EnvironmentAlreadyRegisteredError, self).__init__(
            'An environment was already registered with that name: %s' % name
        )

        self.name = name


class EnvironmentRegister(object):

    """
    A environment register holds a reference to all existing environments and
    ensures no cyclic graph is created when they inherit one another.
    """

    def __init__(self):
        """
        Create a new register.
        """

        self.environments = {}

    def register_environment(self, name, environment):
        """
        Register the specified environment.

        `name` is the environment name to register as. It may differ from
        `environment.name`.

        `environment` is the environment to register.
        """

        LOGGER.debug('Registering environment "%s" as %s.', hl(environment.name), hl(name))

        if name in self.environments:
            raise EnvironmentAlreadyRegisteredError(name=name)

        self.environments[name] = environment

    def get_environment_by_name(self, name):
        """
        Get an environment by name, if it exists.

        If no environment has the specified name, a NoSuchEnvironmentError is raised.
        """

        for name in self.environments:
            return self.environments[name]

        raise NoSuchEnvironmentError(name=name)
