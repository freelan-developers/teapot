"""
tea-party 'Source' class.
"""

from tea_party.log import LOGGER
from tea_party.fetchers import get_fetcher_class_from_shortname, guess_fetcher_instance
from tea_party.fetchers.callbacks import NullFetcherCallback
from tea_party.filters import Filtered


def read_type(_type):
    """
    Read a type in different formats.

    If `_type` is a falsy value, nothing is returned.

    If `_type` is a string, a 2-tuple (`_type`, None) will be returned.

    Otherwise `_type` will be assumed to be an iterable. Its size must not
    exceed 2 elements, and it will be returned as a 2-tuple.
    """

    if not _type:
        return

    if isinstance(_type, basestring):
        return (_type, None)

    if len(_type) == 1:
        return tuple(_type[0], None)
    elif len(_type) == 2:
        return tuple(_type)

    raise ValueError('Incorrect type: %r' % _type)

def make_sources(attendee, sources):
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
                attendee=attendee,
                location=unicode(sources),
                _type=None,
                fetcher_class=guess_fetcher_instance,
                fetcher_options={},
            ),
        ]

    elif isinstance(sources, dict):
        return [
            Source(
                attendee=attendee,
                location=sources.get('location'),
                _type=read_type(sources.get('type')),
                fetcher_class=get_fetcher_class_from_shortname(
                    sources.get('fetcher')
                ),
                fetcher_options=sources.get('fetcher_options'),
                filters=sources.get('filters'),
            ),
        ]

    return sum(map(lambda x: make_sources(attendee, x), sources), [])


class Source(Filtered):

    """
    A Source instance holds information about where and how to get a
    third-party software.
    """

    def __init__(self, attendee, location, _type, fetcher_class, fetcher_options, filters=[]):
        """
        Create a Source instance.

        `attendee` is the attendee this source is attached to.

        `location` is the origin of the third-party software archive to get.
        Its format an meaning depends on the associated `fetcher_class`.

        `_type` is a 2-tuple containing the mimetype, and the encoding of the
        source. If `_type` is falsy, the type will be guessed from the source
        itself.

        `fetcher_options` is a free-format structure that will be passed as a
        parameter to the fetcher on instanciation.

        `filters` is a list of filters that must be truth for the source to be
        active.
        """

        if not attendee:
            raise ValueError('An source must be associated to an attendee.')

        self.attendee = attendee
        self.location = location
        self._type = _type
        self.fetcher_class = fetcher_class
        self.fetcher_options = fetcher_options
        self.__fetcher = None

        Filtered.__init__(self, filters=filters)

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

    def __str__(self):
        """
        Get a string representation of the source.
        """

        return self.location

    @property
    def fetcher(self):
        """
        Get the associated fetcher instance.
        """

        if self.__fetcher is None:
            self.__fetcher = self.fetcher_class(self)

        return self.__fetcher

    def fetch(self, root_path):
        """
        Fetch the specified source.

        Returns dict, containing the information about the archive.
        """

        try:
            cache_info = self.fetcher.fetch(
                target=root_path,
            )

            if self._type:
                cache_info['archive_type'] = self._type

            return cache_info

        except Exception as ex:
            LOGGER.exception(ex)
