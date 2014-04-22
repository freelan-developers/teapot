"""
teapot unit tests.
"""

import os
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from teapot import *
from teapot.memoized import Memoized
from teapot.extensions import parse_extension
from teapot.error import TeapotError


class TestTeapot(unittest.TestCase):

    """
    Tests the different teapot components.
    """

    def setUp(self):
        """
        Clears all memoized instances.
        """

        Memoized.clear_all_instances()

    def test_environments(self):
        """
        Test the environments.
        """

        os.environ['DUMMY'] = 'DUMMY1'
        os.environ['FOO'] = 'FOO1'
        os.environ['HELLO'] = 'HELLO1'

        # We test the variables before we enable the environment
        self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
        self.assertEqual(os.environ.get('FOO'), 'FOO1')
        self.assertEqual(os.environ.get('BAR'), None)
        self.assertEqual(os.environ.get('HELLO'), 'HELLO1')

        # The different environments to test.
        empty_environment = Environment('empty')
        system_environment = Environment('system', variables=os.environ.copy())

        # We test that no variable are propagated inside the empty environment.
        with empty_environment.enable():
            self.assertEqual(os.environ.get('DUMMY'), None)
            self.assertEqual(os.environ.get('FOO'), None)
            self.assertEqual(os.environ.get('BAR'), None)
            self.assertEqual(os.environ.get('HELLO'), None)

        # We test that variables within the system environment are the same
        # than before.
        with system_environment.enable():
            self.assertEqual(os.environ.get('DUMMY'), 'DUMMY1')
            self.assertEqual(os.environ.get('FOO'), 'FOO1')
            self.assertEqual(os.environ.get('BAR'), None)
            self.assertEqual(os.environ.get('HELLO'), 'HELLO1')

        self.assertEqual(system_environment.shell, None)

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
            parent=system_environment,
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
            name='test_environment_sub',
            parent=environment,
            shell=True,
        )

        self.assertEqual(sub_environment.shell, ['my shell'])

        orphan_environment = Environment(
            name='orphan_environment',
            variables={
                'FOO': 'FOO3',
                'BAR': 'BAR1',
                'HELLO': None,
                'NON_EXISTING': None,
            },
            parent=None,
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
            name='shell_environment',
            variables={
                'FOO': 'FOO3',
            },
            parent=system_environment,
            shell=['$FOO'],
        )

        self.assertEqual(shell_environment.shell, ['FOO1'])

        orphan_shell_environment = Environment(
            name='orphan_shell_environment',
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

    def test_filters(self):
        """
        Test the filters.
        """

        f('true', condition=True)
        f('false', condition=False)

        self.assertTrue(f('true'))
        self.assertFalse(f('false'))

        FUNCTION_RESULT = True

        def function():
            return FUNCTION_RESULT

        f('function', condition=function)

        self.assertTrue(f('function'))

        FUNCTION_RESULT = False

        self.assertFalse(f('function'))
        self.assertTrue(f('true') | f('false'))
        self.assertFalse(f('true') & f('false'))
        self.assertFalse(~f('true'))
        self.assertTrue(f('true') ^ f('false'))
        self.assertFalse(f('true') ^ f('true'))
        self.assertFalse(f('false') ^ f('false'))

    def test_attendees(self):
        """
        Test the attendees.
        """

        a = Attendee('a')
        b = Attendee('b')
        c = Attendee('c')
        d = Attendee('d')

        self.assertEqual(a, Attendee('a'))

        a.depends_on('b', c)
        c.depends_on('d')

        self.assertEqual(a.parents, {b, c})
        self.assertEqual(b.parents, set())
        self.assertEqual(c.parents, {d})
        self.assertEqual(d.parents, set())
        self.assertEqual(a.children, set())
        self.assertEqual(b.children, {a})
        self.assertEqual(c.children, {a})
        self.assertEqual(d.children, {c})

        self.assertEqual(
            Attendee.get_dependent_instances(),
            [b, d, c, a],
        )

        self.assertEqual(
            Attendee.get_dependent_instances(['c']),
            [d, c],
        )

        # Create a circular dependency.
        d.depends_on(a)

        self.assertRaises(Attendee.DependencyCycleError, Attendee.get_dependent_instances)

        # Add a source.
        a.add_source('http://some.fake.address')
        self.assertIsNotNone(a.get_source('http://some.fake.address'))

        # Add a build.
        attendee_test_environment = Environment('attendee_test_environment')

        a.add_build('foo', environment='attendee_test_environment')
        self.assertIsNotNone(a.get_build('foo'))
        self.assertEqual(a.get_build('foo').environment, attendee_test_environment)

    def test_extensions(self):
        """
        Test the extensions.
        """

        simple_call = 'foo'
        function_call = 'foo()'
        param_call = 'foo(1, 2, 3)'
        named_param_call = 'foo(a =1,c= 3,b = 2)'
        mixed_call = 'foo ( 1 , c=3, b = "test" )'
        missing_call = 'bar(5, 6, 7)'

        @register_extension('foo')
        def foo(a=None, b=None, c=None):
            return [a, b, c]

        extension, args, kwargs = parse_extension(simple_call)

        self.assertEqual(args, tuple())
        self.assertEqual(kwargs, {})

        extension, args, kwargs = parse_extension(function_call)

        self.assertEqual(args, tuple())
        self.assertEqual(kwargs, {})

        extension, args, kwargs = parse_extension(param_call)

        self.assertEqual(args, (1, 2, 3))
        self.assertEqual(kwargs, {})

        extension, args, kwargs = parse_extension(named_param_call)

        self.assertEqual(args, tuple())
        self.assertEqual(kwargs, {'a': 1, 'b': 2, 'c': 3})

        extension, args, kwargs = parse_extension(mixed_call)

        self.assertEqual(args, (1,))
        self.assertEqual(kwargs, {'b': 'test', 'c': 3})

        # Make sure unregistered extensions don't parse successfully.
        self.assertRaises(TeapotError, parse_extension, missing_call)


if __name__ == '__main__':
    unittest.main()
