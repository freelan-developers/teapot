"""
An attendee class.
"""

import os
import json

from .memoized import MemoizedObject
from .filters import FilteredObject
from .error import TeapotError
from .source import Source
from .log import LOGGER, Highlight as hl
from .options import get_option
from .path import mkdir, rmdir, from_user_path
from .unpackers import Unpacker


class Attendee(MemoizedObject, FilteredObject):

    """
    Represents a project to build.
    """

    propagate_memoization_key = True

    def __init__(self, name, *args, **kwargs):
        self._depends_on = []
        self._sources = []
        self._source = None
        self._cache_manifest = {}
        self._last_parsed_source = None
        self._sources_manifest = {}

        super(Attendee, self).__init__(*args, **kwargs)

    def __repr__(self):
        """
        Get a representation of the attendee.
        """

        return 'Attendee(%r)' % self.name

    def depends_on(self, *attendees):
        """
        Make the attendee depend on one or several other attendees.

        `attendees` is a list of attendees to depend on.
        """

        self._depends_on.extend(attendees)
        return self

    @property
    def cache_path(self):
        return from_user_path(os.path.join(get_option('cache_root'), self.name))

    @property
    def sources_path(self):
        return from_user_path(os.path.join(get_option('sources_root'), self.name))

    @property
    def cache_manifest_path(self):
        return os.path.join(self.cache_path, 'manifest.json')

    @property
    def cache_last_parsed_source_path(self):
        return os.path.join(self.cache_path, 'last_parsed_source.json')

    @property
    def sources_manifest_path(self):
        return os.path.join(self.sources_path, 'manifest.json')

    @property
    def cache_manifest(self):
        if not self._cache_manifest:
            try:
                self._cache_manifest = json.load(open(self.cache_manifest_path))

            except IOError:
                pass

        if not isinstance(self._cache_manifest, dict):
            self._cache_manifest = {}

        return self._cache_manifest

    @cache_manifest.setter
    def cache_manifest(self, value):
        self._cache_manifest = value

        mkdir(self.cache_path)
        json.dump(self._cache_manifest, open(self.cache_manifest_path, 'w'))

    @property
    def last_parsed_source(self):
        if not self._last_parsed_source:
            try:
                self._last_parsed_source = json.load(open(self.cache_last_parsed_source_path))

            except IOError:
                pass

        return self._last_parsed_source

    @last_parsed_source.setter
    def last_parsed_source(self, value):
        self._last_parsed_source = value

        mkdir(self.cache_path)
        json.dump(self._last_parsed_source, open(self.cache_last_parsed_source_path, 'w'))

    @property
    def sources_manifest(self):
        if not self._sources_manifest:
            try:
                self._sources_manifest = json.load(open(self.sources_manifest_path))

            except IOError:
                pass

        if not isinstance(self._sources_manifest, dict):
            self._sources_manifest = {}

        return self._sources_manifest

    @sources_manifest.setter
    def sources_manifest(self, value):
        self._sources_manifest = value

        mkdir(self.sources_path)
        json.dump(self._sources_manifest, open(self.sources_manifest_path, 'w'))

    @property
    def archive_path(self):
        return self.cache_manifest.get('archive_path')

    @property
    def archive_type(self):
        return tuple(self.cache_manifest.get('archive_type', []))

    @property
    def extracted_sources_path(self):
        return self.sources_manifest.get('extracted_sources_path')

    @property
    def must_fetch(self):
        # If the best source changed since last build, `self.source`
        # will clean the cache and the next test will evaluate to true.
        if not self.source:
            return True

        return not self.archive_path or not os.path.isfile(self.archive_path)

    @property
    def must_unpack(self):
        return not self.extracted_sources_path or not os.path.isdir(self.extracted_sources_path)

    @property
    def sources(self):
        """
        Get all the active sources.
        """

        return [x for x in self._sources if x.enabled]

    def add_source(self, resource, *args, **kwargs):
        """
        Add a source to the attendee.

        `resource` is the resource to add to the attendee.
        """

        if self._source is not None:
            LOGGER.debug(
                "Clearing best source %s because a new source was added (%s).",
                hl(self._source),
                hl(resource),
            )

            self._source = None

        if not isinstance(resource, Source):
            resource = Source(resource, *args, **kwargs)

        self._sources.append(resource)
        return self

    def clean_cache(self):
        """
        Clean the cache.
        """

        if os.path.exists(self.cache_path):
            LOGGER.debug(
                "Cache directory for %s is at %s.",
                hl(self),
                hl(self.cache_path),
            )

            rmdir(self.cache_path)
        else:
            LOGGER.debug(
                "Cache directory for %s does not exist at %s. Nothing to do.",
                hl(self),
                hl(self.cache_path),
            )

    def clean_sources(self):
        """
        Clean the sources.
        """

        if os.path.exists(self.sources_path):
            LOGGER.debug(
                "Sources directory for %s is at %s.",
                hl(self),
                hl(self.sources_path),
            )

            rmdir(self.sources_path)
        else:
            LOGGER.debug(
                "Sources directory for %s does not exist at %s. Nothing to do.",
                hl(self),
                hl(self.sources_path),
            )

    @property
    def source(self):
        """
        Get the best source for the attendee.
        """

        if self._source is None:
            LOGGER.debug(
                "Finding best source for %s...",
                hl(self),
            )

            if not self.sources:
                raise TeapotError(
                    (
                        "No enabled source was found for the attendee %s. "
                        "Did you forget to set a filter on the attendee ?"
                    ),
                    hl(self),
                )

            for source in self.sources:
                try:
                    parsed_source = source.parsed_source

                    if parsed_source:
                        if self.last_parsed_source != parsed_source:
                            if self.last_parsed_source:
                                LOGGER.info(
                                    (
                                        "Best source has changed for %s: cleaning "
                                        "cache to trigger a refetch."
                                    ),
                                    hl(self),
                                )
                            else:
                                LOGGER.info(
                                    (
                                        "No previous best source found for %s: "
                                        "making sure the cache is cleaned so a "
                                        "fetch will occur."
                                    ),
                                    hl(self),
                                )

                            self.clean_cache()
                            self.last_parsed_source = parsed_source

                        LOGGER.debug(
                            "Best source for %s is now %s.",
                            hl(self),
                            hl(source),
                        )

                        self._source = source
                        break

                except TeapotError as ex:
                    LOGGER.warning("Error parsing source %s: " + ex.msg, hl(source), *ex.args)
                except Exception as ex:
                    LOGGER.warning("Error parsing source %s: %s", hl(source), hl(str(ex)))

        return self._source

    def fetch(self, force=False):
        """
        Fetch the most appropriate source.

        If `force` is truthy, the archive will be force-fetched again.
        """

        source = self.source

        if self.archive_path:
            if os.path.isfile(self.archive_path):
                if force:
                    LOGGER.info("%s was already fetched but force fetching was requested. Will fetch it again.", hl(self))
                    self.cache_manifest = {}
                else:
                    LOGGER.info("%s was already fetched. Nothing to do.", hl(self))
            else:
                LOGGER.warning("%s was already fetched according to its download manifest but the archive file (%s) was not found. Will fetch it again.", hl(self), self.archive_path)
                self.cache_manifest = {}
        else:
            LOGGER.info("No download manifest found for %s. Will fetch it.", hl(self))

        if not self.cache_manifest:
            LOGGER.info('Fetching %s from %s...', hl(self), hl(source))

            mkdir(self.cache_path)

            self.cache_manifest = source.fetch(target_path=self.cache_path)

            LOGGER.debug("Wrote new cache manifest for %s at: %s", hl(self), hl(self.cache_manifest_path))
            LOGGER.info("%s fetched successfully.", hl(self))

        if not self.cache_manifest:
            raise TeapotError(
                (
                    "All sources failed for the attendee %s. You may want "
                    "to check your network connectivity."
                ),
                hl(self),
            )

        LOGGER.debug(
            "Archive for %s (%s) is at %s",
            hl(self),
            hl(Unpacker.mimetype_to_str(self.archive_type)),
            hl(self.archive_path),
        )

    def unpack(self, force=False):
        """
        Unpack the archive.

        If `force` is truthy, the archive will be force-unpacked again.
        """

        if self.extracted_sources_path:
            if os.path.isdir(self.extracted_sources_path):
                if force:
                    LOGGER.info("%s was already unpacked but force unpacking was requested. Will unpackg it again.", hl(self))
                    self.sources_manifest = {}
                else:
                    LOGGER.info("%s was already unpacked. Nothing to do.", hl(self))
            else:
                LOGGER.warning("%s was already unpacked according to its sources manifest but the extracted sources folder (%s) was not found. Will unpack it again.", hl(self), self.extracted_sources_path)
                self.sources_manifest = {}
        else:
            LOGGER.info("No sources manifest found for %s. Will fetch it.", hl(self))

        if not self.sources_manifest:
            LOGGER.info('Unpacking %s...', hl(self))

            mkdir(self.sources_path)

            LOGGER.debug(
                "Searching appropriate unpacker for archive %s of type %s...",
                hl(self.archive_path),
                hl(Unpacker.mimetype_to_str(self.archive_type)),
            )

            unpacker = Unpacker.get_instance_or_fail(self.archive_type)
            self.sources_manifest = unpacker.unpack(archive_path=self.archive_path, target_path=self.sources_path)

        LOGGER.debug(
            "Archive for %s (%s) is unpacked at %s.",
            hl(self),
            hl(self.archive_path),
            hl(self.extracted_sources_path),
        )
