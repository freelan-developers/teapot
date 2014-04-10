"""
The party classes.
"""

import os
import sys
import imp

from contextlib import contextmanager

from .log import LOGGER
from .log import Highlight as hl
from .attendee import Attendee


def load_party_file(path):
    """
    Load a Party from a file.

    `path` must point to an existing party file.
    """

    path = os.path.abspath(path)

    LOGGER.debug('Importing party file from %r.', path)

    @contextmanager
    def disable_bytecode_generation():
        sentinel, sys.dont_write_bytecode = sys.dont_write_bytecode, True

        try:
            yield
        finally:
            sys.dont_write_bytecode = sentinel

    with disable_bytecode_generation():
        imp.load_source('party', path)


def clean_cache(attendees=None):
    """
    Clean the cache.
    """

    attendees = Attendee.get_enabled_instances(attendees)

    LOGGER.info("Cleaning cache for %s attendee(s)...", hl(len(attendees)))

    for attendee in attendees:
        attendee.clean_cache()

    LOGGER.info("Done cleaning cache for %s attendee(s)...", hl(len(attendees)))


def clean_sources(attendees=None):
    """
    Clean the sources.
    """

    attendees = Attendee.get_enabled_instances(attendees)

    LOGGER.info("Cleaning sources for %s attendee(s)...", hl(len(attendees)))

    for attendee in attendees:
        attendee.clean_sources()

    LOGGER.info("Done cleaning sources for %s attendee(s)...", hl(len(attendees)))


def fetch(attendees=None, force=False):
    """
    Fetch the specified attendees.
    """

    attendees = Attendee.get_enabled_instances(attendees)

    if force:
        LOGGER.info("Force-fetching all %s attendee(s)...", hl(len(attendees)))
    else:
        count = len([x for x in attendees if x.must_fetch])

        if not count:
            LOGGER.info("All attendees were fetched already. Nothing to do.")
            return

        LOGGER.info("Fetching %s out of %s attendee(s)...", hl(count), hl(len(attendees)))

    for attendee in attendees:
        attendee.fetch(force=force)

    LOGGER.info("Done fetching %s attendee(s)...", hl(len(attendees)))


def unpack(attendees=None, force=False):
    """
    Unpack the specified attendees.
    """

    fetch(attendees, force=force)

    attendees = Attendee.get_enabled_instances(attendees)

    if force:
        LOGGER.info("Force-unpacking all %s attendee(s)...", hl(len(attendees)))
    else:
        count = len([x for x in attendees if x.must_unpack])

        if not count:
            LOGGER.info("All attendees were unpacked already. Nothing to do.")
            return

        LOGGER.info("Unpacking %s out of %s attendee(s)...", hl(count), hl(len(attendees)))

    for attendee in attendees:
        attendee.unpack(force=force)

    LOGGER.info("Done unpacking %s attendee(s)...", hl(len(attendees)))
