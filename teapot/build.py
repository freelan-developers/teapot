"""
A build class.
"""

import os

from datetime import datetime
from contextlib import contextmanager

from .memoized import MemoizedObject
from .error import TeapotError
from .log import LOGGER, Highlight as hl
from .filters import FilteredObject
from .environment import Environment


class Build(MemoizedObject, FilteredObject):

    """
    Represents a build.
    """

    memoization_keys = ('attendee', 'name')
    propagate_memoization_keys = True

    @classmethod
    def transform_memoization_keys(cls, attendee, name):
        """
        Make sure the attendee parameter is a real Attendee instance.
        """

        if isinstance(attendee, basestring):
            from .attendee import Attendee

            attendee = Attendee(attendee)

        return attendee, name

    def __init__(self, attendee, name, environment=None, subdir=None, *args, **kwargs):
        super(Build, self).__init__(*args, **kwargs)
        self._environment = environment
        self.subdir = subdir

        # Register the build in the Attendee.
        self.attendee = attendee
        self.name = name
        attendee.add_build(self)

    @property
    def environment(self):
        return Environment(self._environment)

    def __repr__(self):
        """
        Get a representation of the build.
        """

        return 'Build(%r, %r)' % (self.attendee, self.name)

    def __str__(self):
        """
        Get a string representation of the build.
        """

        return '%s_%s' % (self.attendee, self.name)

    @contextmanager
    def create_log_file(self, log_path):
        """
        Create a log file object and returns it.

        `log_path` is the path to the log file to write to.
        """

        try:
            LOGGER.debug('Opening log file at: %s', hl(log_path))

            with open(log_path, 'w') as log_file:
                yield log_file

        finally:
            LOGGER.info('Log file written to: %s', hl(log_path))

    @contextmanager
    def chdir(self, path):
        """
        Change the current directory.
        """

        old_path = os.getcwd()

        LOGGER.debug('Moving to: %s', hl(path))
        os.chdir(path)

        try:
            yield path
        finally:
            LOGGER.debug('Moving back to: %s', hl(old_path))
            os.chdir(old_path)

    def build(self, path, log_path):
        """
        Launch the build in the specified `path`.

        `log_path` is the path to the log file to create.
        """

        working_dir = os.path.join(path, self.subdir if self.subdir else '')

        with self.create_log_file(log_path) as log_file:
            with self.chdir(working_dir):
                LOGGER.info("Build started in %s at %s.", hl(working_dir), hl(datetime.now().strftime('%c')))
                log_file.write("Build started in %s at %s.\n" % (working_dir, datetime.now().strftime('%c')))

                LOGGER.info("Build succeeded at %s.", hl(datetime.now().strftime('%c')))
                log_file.write("Build succeeded at %s.\n" % datetime.now().strftime('%c'))
