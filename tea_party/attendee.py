"""
tea-party 'attendee' class.
"""

import os
import json
import errno

from tea_party.log import LOGGER
from tea_party.source import make_sources
from tea_party.path import mkdir, rmdir
from tea_party.unpackers import get_unpacker_class_for_type
from tea_party.builders import make_builders


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
    attendee.builders = make_builders(attendee, attributes.get('builders'))

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
    BUILD_FILE = 'build.json'

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
        self.builders = []
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

        LOGGER.info('Cleaning cache directory: %s', self.build_path)

        rmdir(self.cache_path)

        LOGGER.info('Done cleaning cache directory for %s.', self)

    def create_cache(self):
        """
        Create the cache directory.
        """

        mkdir(self.cache_path)

    @property
    def build_path(self):
        """
        The path of the source of this attendee.
        """

        return os.path.join(self.party.build_path, self.name)

    def clean_build(self):
        """
        Clean the build directory.
        """

        LOGGER.info('Cleaning build directory: %s', self.build_path)

        rmdir(self.build_path)

        LOGGER.info('Done cleaning build directory for %s.', self)

    def create_build(self):
        """
        Create the build directory.
        """

        mkdir(self.build_path)

    def fetch(self):
        """
        Fetch the attendee archive by trying all its sources.

        If the fetching suceeds, the succeeding source is returned.
        If the fetching fails, a RuntimeError is raised.
        """

        self.create_cache()

        LOGGER.info('Fetching %s...' % self)

        for source in self.sources:
            LOGGER.info('Trying from %s...', source)

            cache_info = source.fetch(root_path=self.cache_path)

            if cache_info:
                LOGGER.info('%s fetched sucessfully.' % self)

                with open(os.path.join(self.cache_path, self.CACHE_FILE), 'w') as cache_file:
                    return json.dump(cache_info, cache_file)

                return source

        raise RuntimeError('All sources failed for %s' % self.name)

    def unpack(self):
        """
        Unpack the attendee archive.

        If the unpacking suceeds, the archive source path is returned.
        """

        self.create_build()

        LOGGER.info('Unpacking %s...' % self)

        build_info = get_unpacker_class_for_type(self.archive_type)(attendee=self).unpack()

        if build_info:
            LOGGER.info('%s unpacked successfully at: %s', self, build_info.get('source_tree_path'))

            with open(os.path.join(self.build_path, self.BUILD_FILE), 'w') as build_file:
                return json.dump(build_info, build_file)

    @property
    def cache(self):
        """
        Get the associated cache info.

        Returns a dict containing the archive cache information.

        If the archive cache information does not exist, an empty dict
        is returned.
        """

        try:
            with open(os.path.join(self.cache_path, self.CACHE_FILE)) as cache_file:
                return json.load(cache_file)

        except IOError as ex:
            if ex.errno != errno.ENOENT:
                raise
        except ValueError:
            pass

        return {}

    @property
    def build(self):
        """
        Get the associated build info.

        Returns a dict containing the archive build information.

        If the archive build information does not exist, an empty dict
        is returned.
        """

        try:
            with open(os.path.join(self.build_path, self.BUILD_FILE)) as build_file:
                return json.load(build_file)

        except IOError as ex:
            if ex.errno != errno.ENOENT:
                raise
        except ValueError:
            pass

        return {}

    @property
    def archive_path(self):
        """
        Get the archive path.
        """

        return self.cache.get('archive_path')

    @property
    def archive_type(self):
        """
        Get the archive type.
        """

        result = self.cache.get('archive_type')

        if result:
            return tuple(result)

    @property
    def fetched(self):
        """
        Check if the attendee was fetched already.
        """

        if self.archive_path and os.path.isfile(self.archive_path):
            LOGGER.debug('%s was already fetched.', self)
            return True

        LOGGER.debug('%s needs fetching.', self)

    @property
    def source_tree_path(self):
        """
        Get the source tree path.
        """

        return self.build.get('source_tree_path')

    @property
    def unpacked(self):
        """
        Check if the attendee needs unpacking.
        """

        if self.source_tree_path and os.path.isdir(self.source_tree_path):
            LOGGER.debug('%s was already unpacked.', self)
            return True

        LOGGER.debug('%s needs unpacking.', self)
