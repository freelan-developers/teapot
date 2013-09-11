"""
tea-party 'attendee' class.
"""

import os
import json
import errno
import shutil

from contextlib import contextmanager

from tea_party.log import LOGGER
from tea_party.log import Highlight as hl
from tea_party.source import make_sources
from tea_party.path import mkdir, rmdir
from tea_party.unpackers import get_unpacker_class_for_type
from tea_party.builders import make_builders
from tea_party.filters import Filtered


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
        filters=attributes.get('filters'),
        prefix=attributes.get('prefix'),
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


class NoSuchBuilderError(ValueError):

    """
    The specified builder does not exist.
    """

    def __init__(self, name=None, tag=None):
        """
        Create an NoSuchBuilderError for the specified `name` or `tag`.
        """

        assert name or tag

        if name:
            super(NoSuchBuilderError, self).__init__(
                'No builder found with that name: %s' % name
            )
        else:
            super(NoSuchBuilderError, self).__init__(
                'No builder found with that tag: %s' % tag
            )

        self.name = name
        self.tag = tag


class Attendee(Filtered):

    """
    An `Attendee` instance holds information about an attendee (third-party
    software).
    """

    CACHE_FILE = 'cache.json'
    BUILD_FILE = 'build.json'

    def __init__(self, party, name, depends=[], filters=[], prefix=None):
        """
        Create an attendee associated to a `party`.

        `name` is the name of the attendee.
        `depends` is a list of Attendee names to depend on.
        `filters` is the list of filters that must match for this attendee to
        be active.
        `prefix` is the prefix to use for that attendee.
        """

        if not party:
            raise ValueError('An attendee must be associated to a party.')

        self.party = party
        self.name = name
        self.sources = []
        self.builders = []
        self.depends = set(depends)
        self.prefix = prefix or ''

        Filtered.__init__(self, filters=filters)

    @property
    def enabled_sources(self):
        """
        Get the list of the enabled sources.
        """

        return [source for source in self.sources if source.enabled]

    @property
    def enabled_builders(self):
        """
        Get the list of the enabled builders.
        """

        return [builder for builder in self.builders if builder.enabled]

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

    def get_builder_by_name(self, name):
        """
        Get all the builders that match the specified name.

        If no builder has the specified name, a NoSuchBuilderError is raised.
        """

        result = [builder for builder in self.builders if builder.name == name]

        if not result:
            raise NoSuchBuilderError(name=name)

        return result[0]

    def get_builders_by_tag(self, tag):
        """
        Get all the enabled builders that match the specified tag.

        If no builder has the specified tag, a NoSuchBuilderError is raised.
        """

        result = [builder for builder in self.enabled_builders if tag in builder.tags]

        if not result:
            raise NoSuchBuilderError(tag=tag)

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

        LOGGER.info('Cleaning cache directory: %s', hl(self.build_path))

        rmdir(self.cache_path)

        LOGGER.info('Done cleaning cache directory for %s.', hl(self))

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

    @property
    def variant_builds_path(self):
        """
        The path to the variant builds.
        """

        return os.path.join(self.build_path, 'builds')

    @property
    def logs_path(self):
        """
        The path to the log files.
        """

        return os.path.join(self.build_path, 'logs')

    def clean_build(self):
        """
        Clean the build directory.
        """

        LOGGER.info('Cleaning build directory: %s', hl(self.build_path))

        rmdir(self.build_path)

        LOGGER.info('Done cleaning build directory for %s.', hl(self))

    def fetch(self):
        """
        Fetch the attendee archive by trying all its sources.

        If the fetching suceeds, the succeeding source is returned.
        If the fetching fails, a RuntimeError is raised.
        """

        self.create_cache()

        LOGGER.info('Fetching %s...', hl(self))

        if not self.enabled_sources:
            raise RuntimeError('No active source found for %s' % self.name)

        for source in self.enabled_sources:
            LOGGER.info('Trying from %s...', hl(source))

            cache_info = source.fetch(root_path=self.cache_path)

            if cache_info:
                LOGGER.success('%s fetched successfully.', hl(self))

                self.write_cache_info(cache_info)

                return source

        raise RuntimeError('All sources failed for %s' % self.name)

    def unpack(self):
        """
        Unpack the attendee archive.

        If the unpacking suceeds, the archive source path is returned.
        """

        mkdir(self.build_path)

        LOGGER.info('Unpacking %s...', hl(self))

        build_info = get_unpacker_class_for_type(self.archive_type)(attendee=self).unpack()

        if build_info:
            LOGGER.success('%s unpacked successfully at: %s', hl(self), hl(build_info.get('source_tree_path')))
            build_info['source_tree_origin_hash'] = self.archive_hash

            self.write_build_info(build_info)

    def build(self, tags=None, verbose=False, keep_builds=False):
        """
        Build the attendee, with the builders that match `tags`, if any.
        """

        if not tags:
            builders = self.enabled_builders
        else:
            builders = map(self.get_builders_by_tag, tags)

        mkdir(self.build_path)
        mkdir(self.logs_path)

        if not builders:
            LOGGER.warning('Not building %s because no builder matches the current settings. Did you forget to set a filter on the attendee ?', hl(self))
        else:
            LOGGER.info('Building %s with %s builder(s)...', hl(self), len(builders))

            for builder in builders:
                try:
                    LOGGER.info('Starting build for %s using builder "%s"...', hl(self), hl(builder))

                    with self.create_temporary_build_directory(builder, persistent=keep_builds) as build_directory:
                        with self.create_log_file(builder) as log_file:
                            builder.build(
                                build_directory=build_directory,
                                log_file=log_file,
                                verbose=verbose,
                            )

                except Exception as ex:
                    LOGGER.error('Error while building %s: %s', hl(self), ex)

                    raise

            LOGGER.success('%s built successfully.', hl(self))

    @contextmanager
    def create_log_file(self, builder):
        """
        Create a log file object and returns it.

        `builder` is the builder that will write to the log file.
        """

        log_file = os.path.join(self.logs_path, '%s.txt' % builder.name)

        try:
            yield open(log_file, 'w')

        finally:
            LOGGER.info('Log file written to: %s', hl(log_file))

    @contextmanager
    def create_temporary_build_directory(self, builder, persistent=False):
        """
        Create a build directory that is a clone of the real build directory.

        The directory name and location depend on the `builder` that will use
        it.

        The directory will be deleted, unless `persistent` is truthy.
        """

        build_directory = os.path.join(self.variant_builds_path, builder.name)

        try:
            rmdir(build_directory)

            LOGGER.info('Copying source tree to %s...', hl(build_directory))
            shutil.copytree(self.source_tree_path, build_directory)

            yield build_directory

        finally:
            if not persistent:
                rmdir(build_directory)
            else:
                LOGGER.info('Keeping build directory at %s', hl(build_directory))

    @property
    def cache_info(self):
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

    def write_cache_info(self, value):
        """
        Write the associated cache info.
        """

        with open(os.path.join(self.cache_path, self.CACHE_FILE), 'w') as cache_file:
            return json.dump(value, cache_file)

    @property
    def build_info(self):
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

    def write_build_info(self, value):
        """
        Set the associated build info.
        """

        with open(os.path.join(self.build_path, self.BUILD_FILE), 'w') as build_file:
            return json.dump(value, build_file)

    @property
    def source_hash(self):
        """
        Get the source hash.
        """

        return self.cache_info.get('source_hash')

    @property
    def archive_path(self):
        """
        Get the archive path.
        """

        return self.cache_info.get('archive_path')

    @property
    def archive_type(self):
        """
        Get the archive type.
        """

        result = self.cache_info.get('archive_type')

        if result:
            return tuple(result)

    @property
    def archive_hash(self):
        """
        Get the archive hash.
        """

        return self.cache_info.get('archive_hash')

    @property
    def fetched(self):
        """
        Check if the attendee was fetched already.
        """

        if self.archive_path and os.path.isfile(self.archive_path):
            return True

    @property
    def source_hash_matches(self):
        """
        Check if one of source hashes match the one in the cache.
        """

        for source in self.enabled_sources:
            if source.source_hash == self.source_hash:
                return True

        return False

    @property
    def source_tree_path(self):
        """
        Get the source tree path.
        """

        return self.build_info.get('source_tree_path')

    @property
    def source_tree_origin_hash(self):
        """
        Get the hash of the archive that was used to create this source tree.
        """

        return self.build_info.get('source_tree_origin_hash')

    @property
    def unpacked(self):
        """
        Check if the attendee needs unpacking.
        """

        if self.source_tree_path and os.path.isdir(self.source_tree_path):
            return True

    @property
    def archive_hash_matches(self):
        """
        Check if the unpacked archive hash matches the one in the cache.
        """

        return self.archive_hash == self.source_tree_origin_hash
