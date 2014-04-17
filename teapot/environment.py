"""
An environment class.
"""

from .memoized import MemoizedObject
from .error import TeapotError
from .log import LOGGER, Highlight as hl


class Environment(MemoizedObject):

    """
    Represents a build environment.
    """

    propagate_memoization_key = True

    def __init__(self, name, *args, **kwargs):
        self._depends_on = None

        super(Environment, self).__init__(*args, **kwargs)

    def __repr__(self):
        """
        Get a representation of the environment.
        """

        return 'Environment(%r)' % self.name

    def depends_on(self, environment):
        """
        Make the environment depend on one other environment.

        `environment` is either a list or an Environment instance.
        """

        self._depends_on = environment
        return self

    @property
    def parent(self):
        """
        Get the parent environment, if any.
        """

        if isinstance(self.depends_on, basestring):
            return self.get_instance_or_fail(self.depends_on)
        elif isinstance(self.depends_on, Environment):
            return self.depends_on
        elif self.depends_on is not None:
            raise TeapotError(
                "An invalid parent %s was specified for environment %s.",
                hl(repr(self.depends_on)),
                hl(self),
            )

    @property
    def children(self):
        """
        Get environments that directly depend on this environment.
        """

        return {
            environment for environment in self.get_instances()
            if self == environment.parent
        }
