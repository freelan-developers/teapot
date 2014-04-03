"""
The party classes.
"""

import os
import sys
import imp

from contextlib import contextmanager

from .log import LOGGER
from .attendee import Attendee


def load_party_file(path):
    """
    Load a Party from a file.

    `path` must point to an existing party file.
    """

    path = os.path.abspath(path)

    LOGGER.debug('Importing party file from %r', path)

    @contextmanager
    def disable_bytecode_generation():
        sentinel, sys.dont_write_bytecode = sys.dont_write_bytecode, True

        try:
            yield
        finally:
            sys.dont_write_bytecode = sentinel

    with disable_bytecode_generation():
        imp.load_source('party', path)


def fetch(attendees=None, force=False):
    """
    Fetches the specified attendees.
    """

    for attendee in Attendee.get_enabled_instances(attendees):
        attendee.fetch()
