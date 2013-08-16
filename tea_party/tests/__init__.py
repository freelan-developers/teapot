"""
tea-party unit tests.
"""

import os
import unittest

from tea_party.party import load_party_file


class TestTeaParty(unittest.TestCase):

    def setUp(self):
        self.fixtures_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'fixtures'
            )
        )
        self.party_file = os.path.join(self.fixtures_path, 'party.yaml')

    def test_parsing(self):
        party = load_party_file(self.party_file)

        attendees_names = set([attendee.name for attendee in party.attendees])

        self.assertEqual(set(['boost', 'libiconv', 'libfoo']), attendees_names)

        print party.attendees
