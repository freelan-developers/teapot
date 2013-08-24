"""
tea-party 'attendee' class.
"""

import os
import json
import errno

from tea_party.log import LOGGER
from tea_party.source import make_sources
from tea_party.path import mkdir, rmdir
from tea_party.unpackers import get_unpacker_class_for_mimetype


def make_attendees(party, data):
    """
    Build a list of attendees from an attendees data dictionary.
    """

    return [
        make_attendee(party, name, attributes)
        for name, attributes
        in data.items()
    ]


def make_attendee(party, name, attributes):
    """
    Create an attendee from a name a dictionary of attributes.
    """

    attendee = Attendee(
        party=party,
        name=name,
        depends=make_depends(attributes.get('depends')),
    )

    attendee.sources = make_sources(attendee, attributes.get('source'))

    return attendee


def make_depends(depends):
    """
    Create a list of dependencies.

    `depends` can either be a single dependency name or a list of dependencies.

    If `depends` is False, an empty list is returned.
    """

    if not depends:
        return []

    elif isinstance(depends, basestring):
        return [depends]

    return depends


class Attendee(object):

    """
    An `Attendee` instance holds information about an attendee (third-party
    software).
    """

    CACHE_FILE = 'cache.json'

    def __init__(self, party, name, depends):
        """
        Create an attendee associated to a `party`.

        `name` is the name of the attendee.
        `depends` is a list of Attendee names to depend on.
        """

        if not party:
            raise ValueError('An attendee must be associated to a party.')

        self.party = party
        self.name = name
        self.sources = []
        self.depends = depends

    def __unicode__(self):
        """
        Get a unicode representation of the attendee.
        """

        return self.name

    def __str__(self):
        """
        Get the name of the attendee.
        """

        return self.name

    def __repr__(self):
        """
        Get a representation of the source.
        """

        return '<%s.%s(party=%r, name=%r, sources=%r, depends=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.party,
            self.name,
            self.sources,
            self.depends,
        )

    @property
    def cache_path(self):
        """
        The path of the cache of this attendee.
        """

        return os.path.join(self.party.cache_path, self.name)

    def clean_cache(self):
        """
        Clean the cache directory.
        """

        rmdir(self.cache_path)

    def create_cache(self):
        """
        Create the cache directory.
        """

        mkdir(self.cache_path)

    @property
    def source_path(self):
        """
        The path of the source of this attendee.
        """

        return os.path.join(self.party.source_path, self.name)

    def clean_source(self):
        """
        Clean the source directory.
        """

        rmdir(self.source_path)

    def create_source(self):
        """
        Create the source directory.
        """

        mkdir(self.source_path)

    def fetch(self):
        """
        Fetch the attendee archive by trying all its sources.

        If the fetching suceeds, the succeeding source is returned.
        If the fetching fails, a RuntimeError is raised.
        """

        self.create_cache()

        for source in self.sources:
            archive_info = source.fetch(root_path=self.cache_path)

            with open(os.path.join(self.cache_path, self.CACHE_FILE), 'w') as cache_file:
                return json.dump(archive_info, cache_file)

            return source

        raise RuntimeError('All sources failed for %s' % self.name)

    def unpack(self):
        """
        Unpack the attendee archive.

        If the unpacking suceeds, the archive source path is returned.
        """

        self.create_source()

        unpacker = get_unpacker_class_for_mimetype((self.cache_info.get('mimetype'), self.cache_info.get('encoding')))()
        unpacker.unpack(self.archive_path)

    @property
    def cache_info(self):
        """
        Get the associated archive info.

        Returns a dict containing the archive information.

        If the archive information or the archive does not exist, nothing is
        returned.
        """

        try:
            with open(os.path.join(self.cache_path, self.CACHE_FILE)) as cache_file:
                return json.load(cache_file)

        except IOError as ex:
            if ex.errno != errno.ENOENT:
                raise
        except ValueError:
            pass

    @property
    def archive_path(self):
        """
        Get the archive path, if an archive exists.
        """

        cache_info = self.cache_info

        if cache_info:
            archive_path = os.path.join(self.cache_path, cache_info.get('archive_path'))

            if os.path.isfile(archive_path):
                return archive_path

    @property
    def needs_fetching(self):
        """
        Check if the attendee needs fetching.
        """

        if self.archive_path:
            LOGGER.debug('%s does not need fetching.', self)
            return False

        LOGGER.debug('%s needs fetching.', self)

        return True

    @property
    def needs_unpacking(self):
        return True
