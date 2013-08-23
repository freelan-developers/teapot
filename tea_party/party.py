"""
tea-party 'party' class.
"""

import os
import yaml

from tea_party.log import LOGGER
from tea_party.attendee import make_attendees
from tea_party.path import read_path, rmdir
from tea_party.defaults import *


def load_party_file(path):
    """
    Create a Party instance from a party-file.

    `path` must be a valid party-file name.
    """

    LOGGER.debug('Opening party-file at %s...' % path)

    with open(path) as party_file:
        data = party_file.read()

    values = yaml.load(data)


    party = Party(
        path=path,
        cache_path=values.get('cache'),
    )

    party.attendees = make_attendees(party, values.get('attendees'))

    return party


class NoSuchAttendeeError(ValueError):

    """
    The specified attendee does not exist.
    """

    def __init__(self, attendee):
        """
        Create an NoSuchAttendeeError for the specified `attendee`.
        """

        super(NoSuchAttendeeError, self).__init__(
            'No such attendee: %s' % attendee
        )


class Party(object):

    """
    A party object is the root object that stores all the information about the
    different attendees (third-party softwares), and the party options.
    """

    def __init__(self, path, cache_path, **kwargs):
        """
        Create a Party instance.

        `path` is the path to the party file.
        `cache_path` is the root of the cache.
        """

        self.path = os.path.abspath(path)
        self.attendees = []
        self.cache_path = read_path(cache_path, os.path.dirname(self.path), DEFAULT_CACHE_PATH)

    def get_attendee_by_name(self, name):
        """
        Get an attendee by name, if it exists.

        If no attendee has the specified name, a NoSuchAttendeeError is raised.
        """

        for attendee in self.attendees:
            if attendee.name == name:
                return attendee

        raise NoSuchAttendeeError(attendee=attendee)

    def clean_cache(self, attendee=None):
        """
        Clean the cache, optionally for a given `attendee` to recover disk
        space.
        """

        if not attendee:
            rmdir(self.cache_path)
        else:
            self.get_attendee_by_name(attendee).clean_cache()

    def fetch(self, force=False, context={}):
        """
        Fetch the archives.
        """

        if force:
            map(lambda x: x.clean_cache(), self.attendees)

        attendees_to_fetch = filter(lambda x: x.needs_fetching(), self.attendees)

        if not attendees_to_fetch:
            LOGGER.info('None of the %s archive(s) needs fetching.', len(self.attendees))

        else:
            LOGGER.info("Fetching %s/%s archive(s)...", len(attendees_to_fetch), len(self.attendees))

            map(lambda x: x.fetch(context), attendees_to_fetch)

            LOGGER.info("Done fetching archives.")

    def unpack(self, force=False, context={}):
        """
        Unpack the archives.
        """

        LOGGER.info('Unpacking %s archive(s)...', len(self.attendees))

        map(lambda x: x.unpack(context), self.attendees)

        LOGGER.info('Done unpacking archives.')
