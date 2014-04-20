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


if __name__ == '__main__':
    unittest.main()
