"""
tea-party 'party' class.
"""

import os
import imp
import yaml

from functools import wraps

from tea_party.log import LOGGER
from tea_party.log import Highlight as hl
from tea_party.attendee import Attendee, make_attendees
from tea_party.path import read_path, rmdir
from tea_party.defaults import *
from tea_party.fetchers.callbacks import ProgressBarFetcherCallback
from tea_party.unpackers.callbacks import ProgressBarUnpackerCallback
from tea_party.environments import make_environments, Environment, EnvironmentRegister, create_default_environment, DEFAULT_ENVIRONMENT_NAME


def load_party_file(path):
    """
    Create a Party instance from a party-file.

    `path` must be a valid party-file name.
    """

    LOGGER.debug('Opening party-file at %s...', hl(path))

    with open(path) as party_file:
        data = party_file.read()

    values = yaml.load(data)

    extension_modules = values.get('extension_modules', {})

    # We import the extension modules.
    #
    # This has to be done first, or the things defined in those extension
    # modules won't be accessible to the parsing functions.

    modules = []

    for name, module_path in extension_modules.items():
        abs_module_path = os.path.join(os.path.dirname(path), module_path)

        try:
            modules.append(imp.load_source(name, abs_module_path))
        except Exception as ex:
            LOGGER.error('Unable to load the extension module "%s" at "%s": %s', hl(name), hl(abs_module_path), ex)

            raise

    party = Party(
        path=path,
        cache_path=values.get('cache_path'),
        build_path=values.get('build_path'),
        prefix=values.get('prefix'),
    )

    party.environments = make_environments(party.environment_register, values.get('environments'))
    party.attendees = make_attendees(party, values.get('attendees'))
    party.modules = modules

    return party


class NoSuchAttendeeError(ValueError):

    """
    The specified attendee does not exist.
    """

    def __init__(self, name):
        """
        Create an NoSuchAttendeeError for the specified `name`.
        """

        super(NoSuchAttendeeError, self).__init__(
            'No such attendee: %s' % name,
        )

        self.name = name


class CyclicDependencyError(ValueError):

    """
    The dependency graph is cyclic.
    """

    def __init__(self, cycle):
        """
        Create a CyclicDependencyError for the specified cycle.
        """

        super(CyclicDependencyError, self).__init__(
            'The attendee dependency graph is cyclic: %s' % ' -> '.join(map(str, cycle)),
        )

        self.cycle = cycle


def has_attendees(func):
    """
    Ensures the function has real attendees instances as its `attendees`
    parameter.
    """

    @wraps(func)
    def result(self, *args, **kwargs):
        attendees = kwargs.get('attendees', [])

        if not attendees:
            attendees = self.enabled_attendees
        else:
            attendees = map(self.get_attendee_by_name, attendees)

        kwargs['attendees'] = attendees

        return func(self, *args, **kwargs)

    return result

def has_ordered_attendees(func):
    """
    Ensures the function gets a list of real attendees instances, ordered, with
    less dependant attendees first.
    """

    @wraps(func)
    def result(self, *args, **kwargs):
        attendees = kwargs.get('attendees', [])

        kwargs['attendees'] = self.get_ordered_attendees(attendees=attendees)

        return func(self, *args, **kwargs)

    return result

class Party(object):

    """
    A party object is the root object that stores all the information about the
    different attendees (third-party softwares), and the party options.
    """

    POST_ACTIONS = []

    @classmethod
    def register_post_action(cls, action):
        """
        Register a post action.

        Post action are called in the registration order, whenever a new Party
        instance is created.
        """

        cls.POST_ACTIONS.append(action)

        return action

    def __init__(self, path=None, cache_path=None, build_path=None, prefix=None, **kwargs):
        """
        Create a Party instance.

        `path` is the path to the party file.
        `cache_path` is the root of the cache.
        `build_path` is the root of the build.
        `prefix` is the prefix common to all attendees.
        """

        self.path = os.path.abspath(path or os.getcwd())
        self.attendees = []
        self.environment_register = EnvironmentRegister()
        self.cache_path = read_path(cache_path, os.path.dirname(self.path), DEFAULT_CACHE_PATH)
        self.build_path = read_path(build_path, os.path.dirname(self.path), DEFAULT_BUILD_PATH)
        self.prefix = read_path(prefix, os.path.dirname(self.path), DEFAULT_PREFIX)
        self.auto_fetch = True
        self.fetcher_callback_class = ProgressBarFetcherCallback
        self.unpacker_callback_class = ProgressBarUnpackerCallback
        self.modules = []

        for post_action in self.POST_ACTIONS:
            post_action(self)

    @property
    def enabled_attendees(self):
        """
        Get the list of the enabled attendees.
        """

        return [attendee for attendee in self.attendees if attendee.enabled]

    def get_attendee_by_name(self, name):
        """
        Get an attendee by name, if it exists.

        If no attendee has the specified name, a NoSuchAttendeeError is raised.
        """

        if isinstance(name, Attendee):
            return name

        for attendee in self.attendees:
            if attendee.name == name:
                return attendee

        raise NoSuchAttendeeError(name=str(name))

    @has_attendees
    def get_ordered_attendees(self, attendees=[]):
        """
        Get a list of attendees ordered in such a way that the less dependent
        attendees start the list.
        """

        graph = {}

        def populate_graph(graph, attendees):

            for attendee in attendees:
                if not attendee.name in graph:
                    graph[attendee.name] = set(attendee.depends)
                    populate_graph(graph, map(self.get_attendee_by_name, attendee.depends))

        populate_graph(graph, attendees)

        ordered_attendees = []

        while graph:

            try:
                attendee = next(node[0] for node in graph.iteritems() if not node[1])

            except StopIteration:
                # We have a cyclic graph. Raise an error and fail.

                cycle = []
                cyclic_graph = graph.copy()

                while cyclic_graph:
                    attendee = next(cyclic_graph.iteritems())[0]

                    if attendee in cycle:
                        break
                    else:
                        cycle.append(attendee)
                        del cyclic_graph[attendee]

                # Reduce the cycle to the smallest sequence.
                cycle = cycle[cycle.index(list(graph[attendee])[0]):]

                cycle = map(self.get_attendee_by_name, cycle)

                raise CyclicDependencyError(cycle=cycle)

            ordered_attendees.append(self.get_attendee_by_name(attendee))
            del graph[attendee]

            for node, depends in graph.iteritems():
                if attendee in depends:
                    depends.remove(attendee)

        return ordered_attendees

    @has_attendees
    def clean_cache(self, attendees=[]):
        """
        Clean the cache, optionally for a given list of `attendees` to recover
        disk space.
        """

        LOGGER.info('Cleaning the cache directory for: %s', hl(', '.join(map(str, attendees))))

        map(Attendee.clean_cache, attendees)

        LOGGER.info('Done cleaning the cache directory.')

    @has_attendees
    def clean_build(self, attendees=[]):
        """
        Clean the build, optionally for a given list of `attendees` to recover
        disk space.
        """

        LOGGER.info('Cleaning the build directory for: %s', hl(', '.join(map(str, attendees))))

        map(Attendee.clean_build, attendees)

        LOGGER.info('Done cleaning the build directory.')

    @has_attendees
    def fetch(self, attendees=[], force=False):
        """
        Fetch the archives.
        """

        if force:
            map(lambda x: x.clean_cache(), attendees)

        attendees_to_fetch = [x for x in attendees if not x.fetched or not x.source_hash_matches]

        for attendee in attendees_to_fetch:
            if not attendee.fetched:
                LOGGER.debug('%s was never fetched. Doing it now.', hl(attendee))
            elif not attendee.source_hash_matches:
                LOGGER.info('The source has changed for %s since it was last fetched. Fetching again.', hl(attendee))

        if not attendees_to_fetch:
            if len(attendees) == 1:
                LOGGER.info('%s was already fetched.', hl(attendees[0]))
            else:
                LOGGER.info('None of the %s archives needs fetching.', len(attendees))

        else:
            LOGGER.info("Fetching %s/%s archive(s)...", len(attendees_to_fetch), len(self.enabled_attendees))

            try:
                map(Attendee.fetch, attendees_to_fetch)
            except Exception as ex:
                LOGGER.error('Error: %s', ex)

                raise RuntimeError('Fetching of %s failed' % self)

            LOGGER.info("Done fetching archives.")

    @has_attendees
    def unpack(self, attendees=[], force=False):
        """
        Unpack the archives.
        """

        if self.auto_fetch:
            self.fetch(attendees=attendees)

        if force:
            map(lambda x: x.clean_build(), attendees)

        attendees_to_unpack = [x for x in attendees if not x.unpacked or not x.archive_hash_matches]

        for attendee in attendees_to_unpack:
            if not attendee.unpacked:
                LOGGER.debug('%s was never unpacked. Doing it now.', hl(attendee))
            elif not attendee.archive_hash_matches:
                LOGGER.info('Source tree hash does not match the archive hash for %s. Unpacking again.', hl(attendee))

        if not attendees_to_unpack:
            if len(attendees) == 1:
                LOGGER.info('%s was already unpacked.', hl(attendees[0]))
            else:
                LOGGER.info('None of the %s archive(s) needs unpacking.', len(attendees))

        else:
            LOGGER.info("Unpacking %s/%s archive(s)...", len(attendees_to_unpack), len(self.enabled_attendees))

            map(Attendee.unpack, attendees_to_unpack)

            LOGGER.info("Done unpacking archives.")

    @has_ordered_attendees
    def build(self, attendees=[], tags=[], verbose=False, force_unpack=False, keep_builds=False, force_build=False):
        """
        Build the archives.
        """

        if self.auto_fetch:
            self.unpack(attendees=attendees, force=force_unpack)

        LOGGER.info("Building %s archive(s)...", len(attendees))

        for attendee in attendees:
            attendee.build(tags=tags, verbose=verbose, keep_builds=keep_builds, force=force_build)

        LOGGER.info("Done building archives.")


@Party.register_post_action
def add_default_environment(party):
    """
    Add the default environment to the party.
    """

    party.environment_register.register_environment(DEFAULT_ENVIRONMENT_NAME, create_default_environment())
