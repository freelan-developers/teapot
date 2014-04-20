"""
A build class.
"""

import os
import re
import signal
import subprocess
import math

from datetime import datetime
from contextlib import contextmanager
from threading import Thread
from datetime import datetime

from .memoized import MemoizedObject
from .error import TeapotError
from .log import LOGGER, Highlight as hl
from .log import print_normal, print_error
from .filters import FilteredObject
from .environment import Environment
from .extensions import parse_extension
from .prefix import PrefixedObject
from .signature import SignableObject


class Build(MemoizedObject, FilteredObject, PrefixedObject, SignableObject):

    """
    Represents a build.
    """

    memoization_keys = ('attendee', 'name')
    propagate_memoization_keys = True
    signature_fields = ('environment', 'subdir', 'commands', 'filter')

    @classmethod
    def transform_memoization_keys(cls, attendee, name):
        """
        Make sure the attendee parameter is a real Attendee instance.
        """

        if isinstance(attendee, basestring):
            from .attendee import Attendee

            attendee = Attendee(attendee)

        return attendee, name

    def __init__(self, attendee, name, environment, subdir=None, commands=None, *args, **kwargs):
        super(Build, self).__init__(*args, **kwargs)
        self._environment = environment
        self.subdir = subdir
        self.commands = commands or []

        # Register the build in the Attendee.
        self.attendee = attendee
        self.name = name
        attendee.add_build(self)

    @property
    def environment(self):
        if not isinstance(self._environment, Environment):
            self._environment = Environment.get_instance(self._environment)

        return self._environment

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

    def add_command(self, command):
        """
        Add a command to the builder.
        """

        self.commands.append(command)

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

    @contextmanager
    def handle_interruptions(self, callable=None):
        """
        Handle interruptions.
        """

        def handler(signum, frame):
            LOGGER.warning('The building process was interrupted by the user.')

            if callable:
                callable()

        previous_handler = signal.signal(signal.SIGINT, handler)

        try:
            yield
        finally:
            signal.signal(signal.SIGINT, previous_handler)

    def build(self, path, log_path, verbose=False):
        """
        Launch the build in the specified `path`.

        `log_path` is the path to the log file to create.
        """

        working_dir = os.path.join(path, self.subdir if self.subdir else '')

        with self.create_log_file(log_path) as log_file:
            with self.chdir(working_dir):
                with self.environment.enable() as env:
                    LOGGER.info("Build started in %s at %s.", hl(working_dir), hl(datetime.now().strftime('%c')))
                    log_file.write("Build started in %s at %s.\n" % (working_dir, datetime.now().strftime('%c')))

                    if env.shell:
                        LOGGER.info('Building within: %s', hl(' '.join(env.shell)))
                        log_file.write('Using "%s" as a shell.\n' % ' '.join(env.shell))
                    else:
                        LOGGER.info('Building within %s.', hl('the default system shell'))
                        log_file.write('Using system shell.\n')

                    for key, value in os.environ.iteritems():
                        LOGGER.debug('%s: %s', key, hl(value))
                        log_file.write('%s: %s\n' % (key, value))

                    for index, command in enumerate(self.commands):
                        command = self.apply_extensions(command)
                        numbered_prefix = ('%%0%sd' % int(math.ceil(math.log10(len(self.commands))))) % index

                        LOGGER.important('%s: %s', numbered_prefix, hl(command))
                        log_file.write('%s: %s\n' % (numbered_prefix, command))

                        if env.shell:
                            process = subprocess.Popen(env.shell + [command], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        else:
                            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                        mixed_output = []

                        with self.handle_interruptions(process.terminate):
                            def read_stdout():
                                for line in iter(process.stdout.readline, ''):
                                    mixed_output.append((print_normal, line))
                                    log_file.write(line)

                                    if verbose:
                                        print_normal(line)

                            def read_stderr():
                                for line in iter(process.stderr.readline, ''):
                                    mixed_output.append((print_error, line))
                                    log_file.write(line)

                                    if verbose:
                                        print_error(line)

                            stdout_thread = Thread(target=read_stdout)
                            stdout_thread.daemon = True
                            stdout_thread.start()

                            stderr_thread = Thread(target=read_stderr)
                            stderr_thread.daemon = True
                            stderr_thread.start()

                            map(Thread.join, [stdout_thread, stderr_thread])
                            process.wait()

                        log_file.write('\n')

                        if process.returncode != 0:
                            if not verbose:
                                for func, line in mixed_output:
                                    func(line)

                            log_file.write('Command failed with status: %s\n' % process.returncode)
                            log_file.write('Build failed at %s.\n' % datetime.now().strftime('%c'))

                            raise subprocess.CalledProcessError(returncode=process.returncode, cmd=command)

                    LOGGER.info("Build succeeded at %s.", hl(datetime.now().strftime('%c')))
                    log_file.write("Build succeeded at %s.\n" % datetime.now().strftime('%c'))

    def apply_extensions(self, command):
        """
        Apply the extensions to the command.
        """

        def replace(match):
            extension, args, kwargs = parse_extension(match.group('extension'))
            return extension(self, *args, **kwargs)

        return re.sub(r'\{{(?P<extension>([^}]|[}][^}])+)}}', replace, command)
