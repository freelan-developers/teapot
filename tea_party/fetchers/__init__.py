"""
Contains all tea-party fetchers logic.

If you want to create your own fetcher, derive from
tea_party.fetchers.base_fetcher.BaseFetcher.
"""

from tea_party.fetchers.base_fetcher import BaseFetcher, UnsupportedLocationError
from tea_party.fetchers.file_fetcher import FileFetcher  # NOQA
from tea_party.fetchers.http_fetcher import HttpFetcher  # NOQA


class NoSuchFetcherError(ValueError):

    """
    Raised when a non-existing fetcher was requested.
    """

    def __init__(self, shortname):
        """
        Create a NoSuchFetcherError instance for the specified `shortname`.
        """

        super(
            NoSuchFetcherError,
            self
        ).__init__(
            'No such fetcher (%r)' % shortname
        )


def get_fetcher_class_from_shortname(shortname):
    """
    Get the appropriate fetcher class/builder from its `shortname`.

    If `shortname` is false, the automatic fetcher builder is returned. See
    guess_fetcher_instance().

    If `shortname` does not match with an existing fetcher shortname, a
    NoSuchFetcherError instance is raised.
    """

    if not shortname or shortname == 'auto':
        return guess_fetcher_instance

    fetcher_class = BaseFetcher.index.get(shortname)

    if fetcher_class:
        return fetcher_class

    raise NoSuchFetcherError(shortname=shortname)


def guess_fetcher_instance(location, default_class=None):
    """
    Guess the fetcher class to use for the specified `location` and returns an
    instance of this class.

    `default_class` can be either a fetcher class or a fetcher shortname to use
    a default if no guess can be made from the specified location.

    If `default_class` is false and no guess can be made, no instance is
    returned.
    """

    if default_class and isinstance(default_class, basestring):
        default_class = get_fetcher_class_from_shortname(default_class)

        if default_class == guess_fetcher_instance:
            raise ValueError(
                'Specifying the auto fetcher class as the default type is not allowed as it could lead to infinite recursion.'
            )

    # We iterate through the registered fetchers classes and try to instantiate
    # one with the location to detect if it is supported.
    for fetcher_class in BaseFetcher.index.values():
        try:
            fetcher_class(location)

            default_class = fetcher_class
            break

        except UnsupportedLocationError:
            pass

    if default_class:
        return default_class(location)
