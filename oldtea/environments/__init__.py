"""
Teapot environments.
"""

import os
import shlex

from teapot.environments.environment_register import EnvironmentRegister
from teapot.environments.environment import Environment


DEFAULT_ENVIRONMENT_NAME = 'default'

def create_default_environment():
    """
    Create a default environment, holding the current process environment
    variables.
    """

    return Environment(name='Default environment', variables=os.environ.copy())

def make_environments(register, environments):
    """
    Make a list of environments from a dictionary.

    If `environments` is a dictionary, make_environment() is called on every
    element, and the result is appended the returned value.

    If `environments` is falsy, an empty list is returned.
    """

    if environments:
        return [
            make_environment(register, name, environment)
            for name, environment
            in environments.items()
        ]

    return []

def make_environment(register, name, environment):
    """
    Make an environment from a dictionary of its attributes.

    `name`, is the name of the environment. If `name` is None, the environment
    is anonymous and won't be registered.

    `environment` is a dictionary of attributes.
    """

    inherit = environment.get('inherit')

    if inherit:
        if isinstance(inherit, basestring):
            inherit = register.get_environment_by_name(inherit)
        else:
            inherit = make_environment(register, None, inherit)

    shell = environment.get('shell', True)

    if shell is not None:
        if isinstance(shell, basestring):
            shell = shlex.split(shell)

    result = Environment(
        name=name,
        variables=environment.get('variables', {}),
        inherit=inherit,
        shell=shell,
    )

    if name:
        register.register_environment(name, result)

    return result
