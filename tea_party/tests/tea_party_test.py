"""
tea_party unit tests.
"""

import os
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from tea_party.party import load_party_file
from tea_party.environments import Environment
from tea_party.extensions import get_extension_by_name, parse_extension
from tea_party.extensions.decorators import named_extension, ExtensionParsingError, DuplicateExtensionError, NoSuchExtensionError


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

    def test_builders(self):
        """
        The the builders.
        """

        #TODO: Parse a real party file and get a builder from it.
        #builder = Builder()
        pass

    def test_environments(self):
        """
        Test the environments.
        """

        os.environ['DUMMY'] = 'DUMMY1'
        os.environ['FOO'] = 'FOO1'
        os.environ['HELLO'] = 'HELLO1'

        default_environment = Environment.get_default(None)

        # We test the variables before we enable the environment
        self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
        self.assertEqual(os.environ.get('FOO'), 'FOO1')
        self.assertEqual(os.environ.get('BAR'), None)
        self.assertEqual(os.environ.get('HELLO'), 'HELLO1')

        # We test that variables within the default environment are the same than before
        with default_environment.enable():
            self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
            self.assertEqual(os.environ.get('FOO'), 'FOO1')
            self.assertEqual(os.environ.get('BAR'), None)
            self.assertEqual(os.environ.get('HELLO'), 'HELLO1')

        self.assertEqual(default_environment.shell, None)

        environment = Environment(
            party=None,
            name='test_environment',
            variables={
                'FOO': 'FOO2',
                'BAR': 'BAR1',
                'HELLO': None,
                'FOO_EXTENDED': '$FOO-$FOO-$NON_EXISTING_VAR-$FOO_EXTENDED',
                'FOO_EXTENDED_PLATFORM': '[%HELLO%]',
            },
            inherit=default_environment,
            shell=['my shell'],
        )

        # We test the variables before we enable the environment
        self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
        self.assertEqual(os.environ.get('FOO'), 'FOO1')
        self.assertEqual(os.environ.get('BAR'), None)
        self.assertEqual(os.environ.get('HELLO'), 'HELLO1')
        self.assertEqual(os.environ.get('FOO_EXTENDED'), None)

        # We apply the environment and test those again
        with environment.enable():
            self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
            self.assertEqual(os.environ.get('FOO'), 'FOO2')
            self.assertEqual(os.environ.get('BAR'), 'BAR1')
            self.assertEqual(os.environ.get('HELLO'), None)
            self.assertEqual(os.environ.get('FOO_EXTENDED'), 'FOO1-FOO1--')

            if sys.platform.startswith('win32'):
                self.assertEqual(os.environ.get('FOO_EXTENDED_PLATFORM'), '[HELLO1]')
            else:
                self.assertEqual(os.environ.get('FOO_EXTENDED_PLATFORM'), '[%HELLO%]')

        self.assertEqual(environment.shell, ['my shell'])

        sub_environment = Environment(
            party=None,
            name='test_environment',
            inherit=environment,
            shell=True,
        )

        self.assertEqual(sub_environment.shell, ['my shell'])

        orphan_environment = Environment(
            party=None,
            name='test_environment',
            variables={
                'FOO': 'FOO3',
                'BAR': 'BAR1',
                'HELLO': None,
            },
            inherit=None,
        )

        # We test the variables before we enable the environment
        self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
        self.assertEqual(os.environ.get('FOO'), 'FOO1')
        self.assertEqual(os.environ.get('BAR'), None)
        self.assertEqual(os.environ.get('HELLO'), 'HELLO1')

        # We apply the environment and test those again
        with orphan_environment.enable():
            self.assertEqual(os.environ.get('DUMMY'), None)
            self.assertEqual(os.environ.get('FOO'), 'FOO3')
            self.assertEqual(os.environ.get('BAR'), 'BAR1')
            self.assertEqual(os.environ.get('HELLO'), 'HELLO1')

        self.assertEqual(orphan_environment.shell, None)

        shell_environment = Environment(
            party=None,
            name='test_environment',
            variables={
                'FOO': 'FOO3',
            },
            inherit=default_environment,
            shell=['$FOO'],
        )

        self.assertEqual(shell_environment.shell, ['FOO1'])

        orphan_shell_environment = Environment(
            party=None,
            name='test_environment',
            variables={
                'FOO': 'FOO3',
            },
            shell=['$FOO'],
        )

        self.assertEqual(orphan_shell_environment.shell, [''])

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
        parse_extension('%s(one, two)' % extension_name, builder='three')

        self.assertEqual(result_dict['foo'], 'one')
        self.assertEqual(result_dict['bar'], 'two')
        self.assertEqual(result_dict['builder'], 'three')

        # Parsing an extension with less than the expected count of parameters raises a TypeError.
        self.assertRaises(TypeError, parse_extension, '%s(one)' % extension_name, builder='two')

        # Parsing an extension with more than the expected count of parameters raises a TypeError.
        self.assertRaises(TypeError, parse_extension, '%s(one, two, three)' % extension_name, builder='four')

        # Parsing an unbalanced extension raises an ExtensionParsingError.
        self.assertRaises(ExtensionParsingError, parse_extension, '%s(one, two' % extension_name, builder='three')

        # Requesting a non-existing extension raises a NoSuchExtensionError.
        self.assertRaises(NoSuchExtensionError, parse_extension, '%s(one, two)' % 'non_existing_extension_name', builder='three')
        self.assertRaises(NoSuchExtensionError, get_extension_by_name, 'non_existing_extension_name')

        # Registering an already existing extension raises a DuplicateExtensionError.
        self.assertRaises(DuplicateExtensionError, named_extension, extension_name)

        # Registering an already existing extension with override does not throw.
        @named_extension(extension_name, override=True)
        def test_extension(builder, foo=None, bar=None):
            result_dict['builder'] = builder
            result_dict['foo'] = foo
            result_dict['bar'] = bar

        # We make sure the extension parsing code works even for function that can take no arguments.
        parse_extension('%s()' % extension_name, builder='one')

        self.assertEqual(result_dict['foo'], None)
        self.assertEqual(result_dict['bar'], None)
        self.assertEqual(result_dict['builder'], 'one')

        # We make sure the extension parsing code works even for function that can take no arguments, when parenthesis are not specified.
        parse_extension(extension_name, builder='two')

        self.assertEqual(result_dict['foo'], None)
        self.assertEqual(result_dict['bar'], None)
        self.assertEqual(result_dict['builder'], 'two')
