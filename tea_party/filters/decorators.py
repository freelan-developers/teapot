"""
The filters decorators.
"""

from functools import wraps


FILTERS = {}

class InvalidFilterError(ValueError):

    """
    No filter exists with the specified name.
    """

    def __init__(self, name):
        """
        Create an InvalidFilterError for the specified filter `name`.
        """

        self.name = name

        super(InvalidFilterError, self).__init__(
            'No filter with the specified name: %s' % name
            )


class DuplicateFilterError(ValueError):

    """
    Another filter with the same name exists.
    """

    def __init__(self, name):
        """
        Create a DuplicateFilterError for the specified filter `name`.
        """

        self.name = name

        super(DuplicateFilterError, self).__init__(
            'Another filter was already registered with the name %r' % name
            )


class named_filter(object):

    """
    Registers a function to be a filter.
    """

    def __init__(self, name, depends=None, override=False):
        """
        Registers the function with the specified name.

        If another function was registered with the same name, a
        DuplicateFilterError will be raised, unless `override` is truthy.
        """

        if name in FILTERS and not override:
            raise DuplicateFilterError(name)

        self.name = name

        if not depends:
            self.depends = []
        elif isinstance(depends, basestring):
            self.depends = [get_filter_by_name(depends)]
        else:
            self.depends = map(get_filter_by_name, depends)

    def __call__(self, func):
        """
        Registers the function and returns it unchanged.
        """

        @wraps(func)
        def decorated(*args, **kwargs):
            return all(f() for f in self.depends + [func])

        FILTERS[self.name] = decorated

        return decorated

def get_filter_by_name(name):
    """
    Get a filter by name.

    If no filter matches the specified name, an InvalidFilterError is raised.
    """

    if not name in FILTERS:
        raise InvalidFilterError(name=name)

    return FILTERS[name]
