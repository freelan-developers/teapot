"""
Defines mechanism to handle options.
"""

from .filters import FilteredObject
from .filters import f_
from .error import TeapotError
from .log import LOGGER
from .log import Highlight as hl


_OPTIONS = {}


class Option(object):
    """
    Defines an option.
    """

    class Value(FilteredObject):
        """
        An option value class.
        """

        def __init__(self, value, *args, **kwargs):
            super(Option.Value, self).__init__(*args, **kwargs)
            self.value = value

    @classmethod
    def get(cls, name):
        option = _OPTIONS.get(name)

        if not option:
            raise TeapotError(
                (
                    "No such registered option \"%s\". Did you forget to "
                    "call `register_option()` ?"
                ),
                name,
            )

        return option

    def __init__(self, name, value_type=str, default_values=[]):
        self.name = name
        self.value_type = value_type
        self._default_values = default_values
        self._values = []

    @property
    def value(self):
        """
        Get the option value.
        """

        values = Option.Value.get_enabled_instances(instances=self._values)

        if not values:
            values = Option.Value.get_enabled_instances(instances=self._default_values)

            if not values:
                LOGGER.debug(
                    (
                        "No value found for option %s that matches the current "
                        "filters. Returning %s instead."
                    ),
                    hl(self.name),
                    hl(repr(None)),
                )
            else:
                LOGGER.debug(
                    (
                        "No value found for option %s that matches the current "
                        "filters. Using defaults instead."
                    ),
                    hl(self.name),
                )

        if len(values) > 1:
            raise TeapotError(
                (
                    "More than one value matches the current filters "
                    "for option %s. Did you forget to set a filter on "
                    "some options ?"
                ),
                hl(self.name),
            )
        elif values:
            return values[0].value

    def add_value(self, value, *args, **kwargs):
        """
        Add a value.

        `value` is the value to add.

        Values are filterable, so you can also specify a `filter` for
        each added value.
        """

        self._values.append(Option.Value(self.value_type(value), *args, **kwargs))


def register_option(name, *args, **kwargs):
    """
    Register an option.

    `name` is the name of the option to register. If an option with that
    name already exists, an exception is thrown.
    """

    if name in _OPTIONS:
        raise TeapotError(
            "The option %s was already registered.",
            hl(name),
        )

    _OPTIONS[name] = Option(name, *args, **kwargs)


def set_option(name, value, *args, **kwargs):
    """
    Set an option.

    `name` is the name of the option to set.
    `value` is the value to set.

    You may specify a `filter` for each value.
    """

    Option.get(name).add_value(value, *args, **kwargs)


def get_option(name):
    """
    Get the value of the option with the specified `name`.
    """

    return Option.get(name).value

# Some built-in options.

register_option('cache_root', default_values=[
    Option.Value('~/.teapot/cache', filter=~f_('windows')),
    Option.Value('%APPDATA%/teapot/cache', filter=f_('windows')),
])
register_option('build_root')
register_option('prefix')
