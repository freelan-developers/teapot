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

    return Party(
        path=path,
        attendees=make_attendees(values.get('attendees', {})),
        cache=make_cache(values.get('cache'), os.path.dirname(path)),
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

        self.path = path
        self.attendees = attendees
