"""
tea-party 'party' class.
"""

import os
import yaml

from tea_party.log import LOGGER
from tea_party.attendee import make_attendees
from tea_party.cache import make_cache


def load_party_file(path):
    """
    Create a Party instance from a party-file.

    `path` must be a valid party-file name.
    """

    LOGGER.debug('Opening party-file at %s...' % path)

    with open(path) as party_file:
        data = party_file.read()

    values = yaml.load(data)

    party_path = os.path.dirname(path)

    return Party(
        path=path,
        attendees=make_attendees(values.get('attendees', {})),
        cache=make_cache(values.get('cache'), party_path),
    )


class Party(object):

    """
    A party object is the root object that stores all the information about the
    different attendees (third-party softwares), and the party options.
    """

    def __init__(self, path, attendees, cache, **kwargs):
        """
        Create a Party instance.

        `path` is the path to the party file.
        `attendees` is a list of attendees.
        `cache` is a tea_party.cache.Cache instance.
        """

        self.path = os.path.abspath(path)
        self.attendees = attendees
        self.cache = cache

    def get_attendee_by_name(self, name):
        """
        Get an attendee by name, if it exists.

        If no attendee has the specified name, nothing is returned.
        """

        for attendee in self.attendees:
            if attendee.name == name:
                return attendee

    def clean(self, attendee=None, clean_archives=False, context={}):
        """
        Clean the build directories to recover disk space.

        If `clean_archives` is specified, archives are erased as well.
        """

        if not attendee:
            if clean_archives:
                self.cache.clean()
            else:
                map(self.cache.clean_attendee_build_directory, self.attendees)
        else:
            if clean_archives:
                self.cache.clean_attendee_directory(self.get_attendee_by_name(attendee))
            else:
                self.cache.clean_attendee_build_directory(self.get_attendee_by_name(attendee))

    def fetch(self, force=False, context={}):
        """
        Fetch the archives.
        """

        if force:
            attendees_to_fetch = self.attendees

            for attendee in self.attendees:
                self.cache.clean_attendee_cache_directory(attendee)

        else:
            attendees_to_fetch = []

            for attendee in self.attendees:
                cache_path = self.cache.get_attendee_cache_directory(attendee)

                if attendee.needs_fetching(cache_path):
                    attendees_to_fetch.append(attendee)

        if not attendees_to_fetch:
            LOGGER.info('None of the %s archive(s) needs fetching.', len(self.attendees))

        else:
            LOGGER.info("Fetching %s/%s archive(s)...", len(attendees_to_fetch), len(self.attendees))

            for attendee in attendees_to_fetch:
                cache_path = self.cache.create_attendee_cache_directory(attendee)
                attendee.fetch(cache_path, context)

            LOGGER.info("Done fetching archives.")

    def unpack(self, context={}):
        """
        Unpack the archives.
        """

        LOGGER.info('Unpacking %s archive(s)...', len(self.attendees))
        LOGGER.info('Done unpacking archives.')
