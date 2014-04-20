"""
An extension class.
"""

from ..memoized import MemoizedObject
from ..error import TeapotError
from ..log import LOGGER, Highlight as hl


class Extension(MemoizedObject):

    """
    Represents an extension.
    """

    def __init__(self, function):
        """
        Define a new extension that uses the specified `function`.
        """

        self._function = function

    def __call__(self, build, *args, **kwargs):
        """
        Call the extension from the specified `build`.
        """

        return str(self._function(build, *args, **kwargs))


class register_extension(object):

    """
    Registers an extension.
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        with Extension.raise_on_duplicate():
            Extension(name=self.name, function=func)

        return func
