"""
tea-party 'Source' class.
"""

from tea_party.log import LOGGER
from tea_party.fetchers import get_fetcher_class_from_shortname, guess_fetcher_instance
from tea_party.fetchers.callbacks import NullFetcherCallback


def make_sources(sources):
    """
    Build a list of Source instances.

    `sources` can be either a simple location string, a dictionary, or an
    iterable of strings and/or dictionaries.

    If `sources` is false, an empty list is returned.
    """

    if not sources:
        return []

    elif isinstance(sources, basestring):
        return [
            Source(
                location=unicode(sources),
                fetcher_class=guess_fetcher_instance,
                fetcher_options={},
            ),
        ]

    elif isinstance(sources, dict):
        return [
            Source(
                location=sources.get('location'),
                fetcher_class=get_fetcher_class_from_shortname(
                    sources.get('fetcher')
                ),
                fetcher_options=sources.get('fetcher_options'),
            ),
        ]

    return sum(map(make_sources, sources), [])


class Source(object):

    """
    A Source instance holds information about where and how to get a
    third-party software.
    """

    def __init__(self, location, fetcher_class, fetcher_options):
        """
        Create a Source instance.

        `location` is the origin of the third-party software archive to get.
        Its format an meaning depends on the associated `fetcher_class`.

        `fetcher_options` is a free-format structure that will be passed as a
        parameter to the fetcher on instanciation.
        """

        self.location = location
        self.fetcher_class = fetcher_class
        self.fetcher_options = fetcher_options
        self.__fetcher = None

    def __repr__(self):
        """
        Get a representation of the source.
        """

        return '<%s.%s(location=%r, fetcher_class=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.location,
            self.fetcher_class,
        )

    @property
    def fetcher(self):
        """
        Get the associated fetcher instance.
        """

        if self.__fetcher is None:
            self.__fetcher = self.fetcher_class(self.location, self.fetcher_options)

        return self.__fetcher

    def fetch(self, root_path, context):
        """
        Fetch the specified source.

        Returns dict, containing the information about the archive.
        """

        try:
            return self.fetcher.fetch(
                target=root_path,
                fetcher_callback_class=context.get('fetcher_callback_class', NullFetcherCallback),
            )

        except Exception as ex:
            LOGGER.exception(ex)
