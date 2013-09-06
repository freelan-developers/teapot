"""
tea_party unit tests.
"""

import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from tea_party.party import load_party_file
from tea_party.extensions import get_extension_by_name, parse_extension
from tea_party.extensions.decorators import named_extension


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
        """
        Test the parsing code.
        """

        party = load_party_file(self.party_file)

        attendees_names = set([attendee.name for attendee in party.attendees])

        self.assertEqual(set(['boost', 'libiconv', 'libfoo']), attendees_names)

    def test_extensions(self):
        """
        Test the extensions.
        """

        extension_name = 'test_extension'
        result_dict = {
            'foo': None,
            'bar': None,
            'builder': None,
        }

        @named_extension(extension_name)
        def test_extension(builder, foo, bar):
            result_dict['builder'] = builder
            result_dict['foo'] = foo
            result_dict['bar'] = bar

        extension = get_extension_by_name(extension_name)

        # We make sure the extension returned is the one we just defined.
        self.assertEqual(extension, test_extension)

        # We make sure the extension parsing code works.
        parse_extension('%s(one, two)' % extension_name, builder="three")

        self.assertEqual(result_dict['foo'], 'one')
        self.assertEqual(result_dict['bar'], 'two')
        self.assertEqual(result_dict['builder'], 'three')
