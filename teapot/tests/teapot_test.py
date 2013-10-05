"""
teapot unit tests.
"""

import os
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from teapot.party import Party, NoSuchAttendeeError, CyclicDependencyError, load_party_file
from teapot.attendee import Attendee
from teapot.fetchers.callbacks import NullFetcherCallback
from teapot.unpackers.callbacks import NullUnpackerCallback
from teapot.environments import Environment, EnvironmentRegister, create_default_environment
from teapot.environments.environment_register import NoSuchEnvironmentError, EnvironmentAlreadyRegisteredError
from teapot.extensions import get_extension_by_name, parse_extension
from teapot.extensions.decorators import named_extension, ExtensionParsingError, DuplicateExtensionError, NoSuchExtensionError


class TestTeapot(unittest.TestCase):

    def setUp(self):
        """
        Set up tests.
        """

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

        party.fetcher_callback_class = NullFetcherCallback
        party.unpacker_callback_class = NullUnpackerCallback

        # Test the attendees.
        self.assertEqual(
            set([attendee.name for attendee in party.attendees]),
            set(['alpha', 'beta', 'gamma']),
        )

        alpha = party.get_attendee_by_name('alpha')
        beta = party.get_attendee_by_name('beta')
        gamma = party.get_attendee_by_name('gamma')

        self.assertEqual(len(alpha.sources), 1)
        self.assertEqual(len(alpha.builders), 3)
        self.assertEqual(len(alpha.enabled_builders), 2)

        self.assertEqual(len(beta.sources), 1)
        self.assertEqual(len(beta.builders), 1)
        self.assertEqual(len(beta.enabled_builders), 1)

        self.assertEqual(len(gamma.sources), 2)
        self.assertEqual(len(gamma.depends), 2)
        self.assertEqual(len(gamma.builders), 0)
        self.assertEqual(len(gamma.enabled_builders), 0)

        # Signature changes tests
        signatures = [builder.signature for builder in alpha.builders]

        # Changing filters should not change signature
        for builder in alpha.builders:
            builder.filters[:] = []

        for signature, builder in zip(signatures, alpha.builders):
            self.assertEqual(signature, builder.signature)

        # Changing commands must change the signature
        for builder in alpha.builders:
            builder.commands.append('foo')

        for signature, builder in zip(signatures, alpha.builders):
            self.assertNotEqual(signature, builder.signature)

        signatures = [builder.signature for builder in alpha.builders]

        # Changing prefix must change the signature
        for builder in alpha.builders:
            builder.prefix += 'foo'

        for signature, builder in zip(signatures, alpha.builders):
            self.assertNotEqual(signature, builder.signature)

        signatures = [builder.signature for builder in alpha.builders]

        # Changing environment must change the signature
        for builder in alpha.builders:
            builder.environment.variables['NEWVARIABLE'] = 'foo'

        for signature, builder in zip(signatures, alpha.builders):
            self.assertNotEqual(signature, builder.signature)

    def test_party(self):
        """
        The the party object.
        """

        def attendee_name(num):
            return 'attendee #%s' % num

        party = Party()

        # First test with a broken dependency graph.
        party.attendees = [
            Attendee(
                party=party,
                name=attendee_name(i),
                depends=[attendee_name(i + 1)],
            )
            for i in range(5)
        ]

        attendees_copy = list(party.attendees)

        with self.assertRaises(NoSuchAttendeeError) as context:
            party.get_ordered_attendees()

        self.assertEqual(context.exception.name, attendee_name(5))
        self.assertEqual(attendees_copy, party.attendees)

        # Test with a cyclic dependency graph.
        party.attendees.append(
            Attendee(
                party=party,
                name=attendee_name(5),
                depends=[attendee_name(2)],
            ),
        )

        attendees_copy = list(party.attendees)

        with self.assertRaises(CyclicDependencyError) as context:
            party.get_ordered_attendees()

        self.assertEqual(context.exception.cycle, party.attendees[2:])
        self.assertEqual(attendees_copy, party.attendees)

        # Test with a complete dependency graph.
        party.attendees[3].depends = []

        attendees_copy = list(party.attendees)

        self.assertEqual(
            party.get_ordered_attendees(),
            [party.attendees[i] for i in (3, 2, 1, 0, 5, 4)],
        )

        self.assertEqual(attendees_copy, party.attendees)

        self.assertEqual(
            party.get_ordered_attendees(attendees=[attendee_name(0)]),
            [party.attendees[i] for i in (3, 2, 1, 0)],
        )

        self.assertEqual(attendees_copy, party.attendees)

        self.assertEqual(
            party.get_ordered_attendees(attendees=[attendee_name(5), attendee_name(1)]),
            [party.attendees[i] for i in (3, 2, 1, 5)],
        )

        self.assertEqual(attendees_copy, party.attendees)


    def test_environments(self):
        """
        Test the environments.
        """

        os.environ['DUMMY'] = 'DUMMY1'
        os.environ['FOO'] = 'FOO1'
        os.environ['HELLO'] = 'HELLO1'

        default_environment = create_default_environment()

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
            name='test_environment',
            variables={
                'FOO': 'FOO2',
                'BAR': 'BAR1',
                'HELLO': None,
                'FOO_EXTENDED': '$FOO-$FOO-$NON_EXISTING_VAR-$FOO_EXTENDED',
                'FOO_EXTENDED_PLATFORM': '[%HELLO%]',
                'NON_EXISTING': None,
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
        self.assertTrue('NON_EXISTING' not in os.environ)

        # We apply the environment and test those again
        with environment.enable():
            self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
            self.assertEqual(os.environ.get('FOO'), 'FOO2')
            self.assertEqual(os.environ.get('BAR'), 'BAR1')
            self.assertEqual(os.environ.get('HELLO'), None)
            self.assertEqual(os.environ.get('FOO_EXTENDED'), 'FOO1-FOO1--')
            self.assertTrue('NON_EXISTING' not in os.environ)

            if sys.platform.startswith('win32'):
                self.assertEqual(os.environ.get('FOO_EXTENDED_PLATFORM'), '[HELLO1]')
            else:
                self.assertEqual(os.environ.get('FOO_EXTENDED_PLATFORM'), '[%HELLO%]')

        self.assertEqual(environment.shell, ['my shell'])

        sub_environment = Environment(
            name='test_environment',
            inherit=environment,
            shell=True,
        )

        self.assertEqual(sub_environment.shell, ['my shell'])

        orphan_environment = Environment(
            name='test_environment',
            variables={
                'FOO': 'FOO3',
                'BAR': 'BAR1',
                'HELLO': None,
                'NON_EXISTING': None,
            },
            inherit=None,
        )

        # We test the variables before we enable the environment
        self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
        self.assertEqual(os.environ.get('FOO'), 'FOO1')
        self.assertEqual(os.environ.get('BAR'), None)
        self.assertEqual(os.environ.get('HELLO'), 'HELLO1')
        self.assertTrue('NON_EXISTING' not in os.environ)

        # We apply the environment and test those again
        with orphan_environment.enable():
            self.assertEqual(os.environ.get('DUMMY'), None)
            self.assertEqual(os.environ.get('FOO'), 'FOO3')
            self.assertEqual(os.environ.get('BAR'), 'BAR1')
            self.assertEqual(os.environ.get('HELLO'), 'HELLO1')
            self.assertTrue('NON_EXISTING' not in os.environ)

        self.assertEqual(orphan_environment.shell, None)

        shell_environment = Environment(
            name='test_environment',
            variables={
                'FOO': 'FOO3',
            },
            inherit=default_environment,
            shell=['$FOO'],
        )

        self.assertEqual(shell_environment.shell, ['FOO1'])

        orphan_shell_environment = Environment(
            name='test_environment',
            variables={
                'FOO': 'FOO3',
            },
            shell=['$FOO'],
        )

        self.assertEqual(orphan_shell_environment.shell, [''])

        # Test signatures changes

        signature = environment.signature
        sub_signature = sub_environment.signature

        environment.variables['NEWVARIABLE'] = 'bar'

        self.assertNotEqual(signature, environment.signature)
        self.assertNotEqual(sub_environment, sub_environment.signature)

        signature = environment.signature
        sub_signature = sub_environment.signature

        environment.shell = ['foo', 'goo']

        self.assertNotEqual(signature, environment.signature)
        self.assertNotEqual(sub_environment, sub_environment.signature)

        signature = environment.signature
        sub_signature = sub_environment.signature

        sub_environment.variables['NEWVARIABLE'] = 'bar'

        self.assertEqual(signature, environment.signature)
        self.assertNotEqual(sub_environment, sub_environment.signature)

        signature = environment.signature
        sub_signature = sub_environment.signature

        sub_environment.shell = ['foo', 'goo', 'boo']

        self.assertEqual(signature, environment.signature)
        self.assertNotEqual(sub_environment, sub_environment.signature)

    def test_environment_register(self):
        """
        Test the environment register.
        """

        register = EnvironmentRegister()

        with self.assertRaises(NoSuchEnvironmentError) as context:
            register.get_environment_by_name('foo')

        self.assertEqual(context.exception.name, 'foo')

        environments = []

        for index in xrange(50):
            environment = Environment(
                name='test_environment_%s' % index,
            )

            environments.append(environment)
            register.register_environment('env%s' % index, environment)

        with self.assertRaises(EnvironmentAlreadyRegisteredError) as context:
            register.register_environment('env5', environment)

        self.assertEqual(context.exception.name, 'env5')

        for index, environment in enumerate(environments):
            self.assertEqual(register.get_environment_by_name('env%s' % index), environment)

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

if __name__ == '__main__':
    unittest.main()
