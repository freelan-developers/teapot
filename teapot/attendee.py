"""
An attendee class.
"""

import os
import json
import hashlib

from .memoized import MemoizedObject
from .filters import FilteredObject
from .source import Source
from .error import TeapotError
from .log import LOGGER, Highlight as hl
from .options import get_option
from .path import mkdir, rmdir, from_user_path, temporary_copy
from .unpackers import Unpacker
from .build import Build
from .globals import get_party_path
from .prefix import PrefixedObject


class Attendee(MemoizedObject, FilteredObject, PrefixedObject):

    """
    Represents a project to build.
    """

    class DependencyCycleError(TeapotError):
        def __init__(self, cycle):
            cycle_str = ' -> '.join(map(str, cycle))

            super(Attendee.DependencyCycleError, self).__init__(
                'Dependency cycle found: %s',
                hl(cycle_str)
            )

            self.cycle = cycle

    @classmethod
    def get_dependent_instances(cls, keys_list=None):
        """
        Get the dependent instances, less dependent instances first.
        """

        try:
            instances = cls.get_enabled_instances(keys_list=keys_list)
        except Attendee.NoSuchInstance as ex:
            raise TeapotError(
                (
                    "Reference to a non-existing attendee %s could not be "
                    "resolved."
                ),
                hl(ex.keys[0]),
            )

        result = []
        dependency_tree = {
            attendee: attendee.parents
            for attendee in cls.get_enabled_instances()
        }

        while dependency_tree:
            try:
                attendee = next(x[0] for x in dependency_tree.iteritems() if not x[1])
            except StopIteration:
                # We can't find an attendee that does not depend on any
                # other. We have a dependency cycle.
                cycle = []
                attendee = dependency_tree.keys()[0]

                while not attendee in cycle:
                    cycle.append(attendee)
                    attendee = next(iter(dependency_tree[attendee]))

                # We make sure the dependency cycle starts with the
                # first repeating element (which is currently in
                # `attendee`)
                cycle = cycle[cycle.index(attendee):] + [attendee]

                raise Attendee.DependencyCycleError(cycle)

            else:
                result.append(attendee)
                del dependency_tree[attendee]

                dependency_tree = {
                    key: value - {attendee}
                    for key, value in dependency_tree.iteritems()
                }

        unneeded_results = set(result)

        def filter_out(instance):
            if instance in unneeded_results:
                unneeded_results.remove(instance)
                map(filter_out, instance.parents)

        map(filter_out, instances)

        return [x for x in result if x not in unneeded_results]

    def __init__(self, *args, **kwargs):
        self.party_path = get_party_path()
        self._depends_on = []
        self._sources = []
        self._source = None
        self._cache_manifest = {}
        self._last_parsed_source = None
        self._sources_manifest = {}
        self._last_unpacked_archive_info = {}
        self._builds = set()
        self._builds_manifest = {}

        super(Attendee, self).__init__(*args, **kwargs)

    def __repr__(self):
        """
        Get a representation of the attendee.
        """

        return 'Attendee(%r)' % self.name

    @property
    def party_root(self):
        return os.path.dirname(self.party_path)

    def depends_on(self, *attendees):
        """
        Make the attendee depend on one or several other attendees.

        `attendees` is a list of attendees to depend on.
        """

        self._depends_on.extend(attendees)
        return self

    @property
    def parents(self):
        """
        Get attendees this attendee directly depends on.
        """

        try:
            return set(self.get_enabled_instances(keys_list=self._depends_on))
        except Attendee.NoSuchInstance as ex:
            raise TeapotError(
                (
                    "Reference to a non-existing parent attendee %s could not "
                    "be resolved in attendee %s."
                ),
                hl(ex.keys[0]),
                hl(self),
            )

    @property
    def children(self):
        """
        Get attendees that directly depends on this attendee.
        """

        return {
            attendee for attendee in self.get_enabled_instances()
            if self in attendee.parents
        }

    @property
    def cache_path(self):
        return from_user_path(os.path.join(get_option('cache_root'), self.name))

    @property
    def sources_path(self):
        return from_user_path(os.path.join(get_option('sources_root'), self.name))

    @property
    def builds_path(self):
        return from_user_path(os.path.join(get_option('builds_root'), self.name))

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
    def sources_last_unpacked_archive_info_path(self):
        return os.path.join(self.sources_path, 'last_unpacked_archive_info.json')

    @property
    def builds_manifest_path(self):
        return os.path.join(self.builds_path, 'manifest.json')

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
    def last_unpacked_archive_info(self):
        if not self._last_unpacked_archive_info:
            try:
                self._last_unpacked_archive_info = json.load(open(self.sources_last_unpacked_archive_info_path))

            except IOError:
                pass

        return self._last_unpacked_archive_info

    @last_unpacked_archive_info.setter
    def last_unpacked_archive_info(self, value):
        self._last_unpacked_archive_info = value

        mkdir(self.sources_path)
        json.dump(self._last_unpacked_archive_info, open(self.sources_last_unpacked_archive_info_path, 'w'))

    @property
    def builds_manifest(self):
        if not self._builds_manifest:
            try:
                self._builds_manifest = json.load(open(self.builds_manifest_path))

            except IOError:
                pass

        if not isinstance(self._builds_manifest, dict):
            self._builds_manifest = {}

        return self._builds_manifest

    @builds_manifest.setter
    def builds_manifest(self, value):
        self._builds_manifest = value

        mkdir(self.builds_path)
        json.dump(self._builds_manifest, open(self.builds_manifest_path, 'w'))

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
        if not self.check_archive_signature():
            return True

        return not self.extracted_sources_path or not os.path.isdir(self.extracted_sources_path)

    @property
    def must_build(self):
        for build in self.builds:
            if self.builds_manifest.get(build.name) != build.signature:
                return True

        return False

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
                hl(source),
            )

            self._source = None

        if not isinstance(resource, Source):
            resource = Source(self, resource, *args, **kwargs)
        else:
            self._sources.append(resource)

        return self

    def get_source(self, resource):
        """
        Get a source.
        """

        return Source.get_instance_or_fail(self, resource)

    @property
    def builds(self):
        """
        Get all the active builds.
        """

        return [x for x in self._builds if x.enabled]

    def add_build(self, build, *args, **kwargs):
        """
        Add a build to the attendee.
        """

        if not isinstance(build, Build):
            build = Build(self, build, *args, **kwargs)
        else:
            self._builds.add(build)

        return self

    def get_build(self, build):
        """
        Get a build.
        """

        return Build.get_instance_or_fail(self, build)

    def clean(self):
        """
        Clean everything.
        """

        self.clean_cache()
        self.clean_sources()
        self.clean_builds()

    def clean_cache(self):
        """
        Clean the cache.
        """

        if os.path.exists(self.cache_path):
            LOGGER.info("Cleaning cache directory for %s.", hl(self))
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
            LOGGER.info("Cache directory for %s is already cleaned.", hl(self))

    def clean_sources(self):
        """
        Clean the sources.
        """

        if os.path.exists(self.sources_path):
            LOGGER.info("Cleaning sources directory for %s.", hl(self))
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
            LOGGER.info("Sources directory for %s is already cleaned.", hl(self))

    def clean_builds(self):
        """
        Clean the builds.
        """

        if os.path.exists(self.builds_path):
            LOGGER.info("Cleaning builds directory for %s.", hl(self))
            LOGGER.debug(
                "Builds directory for %s is at %s.",
                hl(self),
                hl(self.builds_path),
            )

            rmdir(self.builds_path)
        else:
            LOGGER.debug(
                "Builds directory for %s does not exist at %s. Nothing to do.",
                hl(self),
                hl(self.builds_path),
            )
            LOGGER.info("Builds directory for %s is already cleaned.", hl(self))

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
                    LOGGER.warning("Error parsing source %s: " + ex.msg, hl(source), *ex.msg_args)
                except Exception as ex:
                    LOGGER.warning("Error parsing source %s: %s", hl(source), hl(str(ex)))

        return self._source

    def check_archive_signature(self):
        """
        Check the archive signature.
        """

        m = hashlib.sha1()

        def compute_hash(path):
            if os.path.isfile(path):
                with open(path) as f:
                    for s in iter(lambda: f.read(1024 ** 2), ''):
                        m.update(s)
            else:
                for root, dirs, files in os.walk(self.archive_path):
                    for f in files:
                        compute_hash(os.path.join(root, f))

        compute_hash(self.archive_path)
        archive_signature = m.hexdigest()

        def update_signature():
            # This has to be done in this order or it won't work.
            self.clean_sources()

            LOGGER.debug(
                "Writing new archive signature for %s: %s",
                hl(self.archive_path),
                hl(archive_signature),
            )

            self.last_unpacked_archive_info = {
                'archive_signature': archive_signature,
            }

        archive_info = self.last_unpacked_archive_info

        if not archive_info:
            LOGGER.info(
                (
                    "No previous archive signature found for %s. Making sure "
                    "the sources directory gets cleaned."
                ),
                hl(self),
            )
            update_signature()
            return False

        last_archive_signature = archive_info.get('archive_signature')

        if archive_signature != last_archive_signature:
            LOGGER.info(
                (
                    "Archive signature for %s changed from %s to %s. Cleaning "
                    "the sources to make sure they get unpacked again."
                ),
                hl(self),
                hl(last_archive_signature),
                hl(archive_signature),
            )

            update_signature()
            return False

        LOGGER.debug(
            (
                "Archive signature for %s matches the last known one (%s). No "
                "cleaning of the sources needed."
            ),
            hl(self.archive_path),
            hl(archive_signature),
        )

        return True

    def fetch(self, force=False):
        """
        Fetch the most appropriate source.

        If `force` is truthy, the archive will be force-fetched again.
        """

        source = self.source

        if not source:
            self.cache_manifest = {}
            raise TeapotError("No valid source was found for %s. Unable to fetch.", hl(self))

        if self.archive_path:
            if os.path.exists(self.archive_path):
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
                    LOGGER.info("%s was already unpacked but force unpacking was requested. Will unpack it again.", hl(self))
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

            LOGGER.debug('Clearing builds manifest as unpacking just took place.')
            self.builds_manifest = {}

        LOGGER.debug(
            "Archive for %s (%s) is unpacked at %s.",
            hl(self),
            hl(self.archive_path),
            hl(self.extracted_sources_path),
        )

    def build(self, force=False, verbose=False, keep_builds=False):
        """
        Build the attendee.

        If `force` is truthy, the archive will be force-built again.
        """

        for build in self.builds:
            last_signature = self.builds_manifest.get(build.name)
            signature = build.signature

            if last_signature is None:
                LOGGER.info(
                    "No known build signature for %s. Will build it.",
                    hl(build),
                )
            elif last_signature != signature:
                LOGGER.info(
                    "Last signature for %s (%s) does not match the current one (%s). Will build it again.",
                    hl(build),
                    hl(last_signature),
                    hl(signature),
                )
            elif force:
                LOGGER.info(
                    "Last signature for %s matches the current one (%s) but force-build requested. Will build it again.",
                    hl(build),
                    hl(signature),
                )
                self.builds_manifest[build.name] = None
                # Forces manifest writing.
                self.builds_manifest = self.builds_manifest
            else:
                LOGGER.info(
                    "%s was built already. Nothing to do.",
                    hl(build),
                )
                return

            build_path = os.path.join(self.builds_path, build.name)
            log_path = os.path.join(self.builds_path, build.name + '.log')

            with temporary_copy(self.extracted_sources_path, build_path, persistent=keep_builds):
                build.build(path=build_path, log_path=log_path, verbose=verbose)

                LOGGER.debug('Setting last build signature to: %s', hl(signature))
                self.builds_manifest[build.name] = signature
                # Forces manifest writing.
                self.builds_manifest = self.builds_manifest
