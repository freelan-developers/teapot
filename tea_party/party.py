"""
tea-party 'party' class.
"""

import yaml

from tea_party.attendee import make_attendees


def load_party_file(path):
    """
    Create a Party instance from a party-file.

    `path` must be a valid party-file name.
    """

    with open(path) as party_file:
        data = party_file.read()

    values = yaml.load(data)

    return Party(
        attendees=make_attendees(values.get('attendees', {})),
    )


class Party(object):

    """
    A party object is the root object that stores all the information about the
    different attendees (third-party softwares), and the party options.
    """

    def __init__(self, attendees, **kwargs):
        """
        Create a Party instance from a list of attendees.
        """

        self.attendees = attendees
