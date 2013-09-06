"""
Tea-party environments.
"""


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

    `name`, is the name of the environment.

    `environment` is a dictionary of attributes.
    """

    return Environment(
        party=party,
        name=name,
        variables=environment.get('variables', {}),
        inherit=environment.get('inherit', True),
        shell=environment.get('shell'),
    )

class Environment(object):

    """
    Represents an environment for builders.
    """

    def __init__(self, party, name, variables=None, inherit=True, shell=None):
        """
        Initialize a new Environment.

        `party` is the party instance to which the environment belongs.

        `name`, is the name of the environment.

        `variables`, if specified, is a map of the variables and their values.

        If `inherit` is truthy (which it is by default), variables with a None
        value are removed from the environment.

        If `inherits` is falsy, only the variables in `variables` will be
        passed to the environment, and those with a None value will be passed
        with their inherited value.

        `shell`, if specified, is the shell to use to execute the commands
        during builds.
        """

        self.party = party
        self.name = name
        self.variables = variables or {}
        self.inherit = bool(inherit)
        self.shell = shell
