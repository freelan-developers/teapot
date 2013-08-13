"""
three-party unit tests.
"""

import os
import unittest

from three_party.party import Party, load_party

class TestThreeParty(unittest.TestCase):

    def setUp(self):
        self.fixtures_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures'))
        self.party_file = os.path.join(self.fixtures_path, 'party.yaml')

    def test_parsing(self):
        party = load_party(self.party_file)
        self.assertIn('boost', party.attendees)
        self.assertIn('libiconv', party.attendees)
