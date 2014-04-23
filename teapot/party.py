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
from .globals import set_party_path


@contextmanager
def disable_bytecode_generation():
    """
    Temporarily disable bytecode generation.
    """
    sentinel, sys.dont_write_bytecode = sys.dont_write_bytecode, True

    try:
        yield
    finally:
        sys.dont_write_bytecode = sentinel


def load_party_file(path):
    """
    Load a Party from a file.

    `path` must point to an existing party file.
    """

    path = os.path.abspath(path)

    LOGGER.debug('Importing party file from %r.', path)

    with disable_bytecode_generation():
        with set_party_path(path):
            imp.load_source('party', path)

    LOGGER.debug('Done importing party file.')


def clean_all(attendees=None):
    """
    Clean everything.
    """

    attendees = Attendee.get_enabled_instances(attendees or None)

    LOGGER.info("Cleaning everything for %s attendee(s)...", hl(len(attendees)))

    clean_cache(attendees)
    clean_sources(attendees)
    clean_builds(attendees)

    LOGGER.info("Done cleaning everything for %s attendee(s)...", hl(len(attendees)))


def clean_cache(attendees=None):
    """
    Clean the cache.
    """

    attendees = Attendee.get_enabled_instances(attendees or None)

    LOGGER.info("Cleaning cache for %s attendee(s)...", hl(len(attendees)))

    for attendee in attendees:
        attendee.clean_cache()

    LOGGER.info("Done cleaning cache for %s attendee(s)...", hl(len(attendees)))


def clean_sources(attendees=None):
    """
    Clean the sources.
    """

    attendees = Attendee.get_enabled_instances(attendees or None)

    LOGGER.info("Cleaning sources for %s attendee(s)...", hl(len(attendees)))

    for attendee in attendees:
        attendee.clean_sources()

    LOGGER.info("Done cleaning sources for %s attendee(s)...", hl(len(attendees)))


def clean_builds(attendees=None):
    """
    Clean the builds.
    """

    attendees = Attendee.get_enabled_instances(attendees or None)

    LOGGER.info("Cleaning builds for %s attendee(s)...", hl(len(attendees)))

    for attendee in attendees:
        attendee.clean_builds()

    LOGGER.info("Done cleaning builds for %s attendee(s)...", hl(len(attendees)))


def fetch(attendees=None, force=False):
    """
    Fetch the specified attendees.
    """

    attendees = Attendee.get_dependent_instances(attendees or None)

    if force:
        LOGGER.info("Force fetch requested...")
    else:
        attendees = [x for x in attendees if x.must_fetch]

        if not attendees:
            LOGGER.info("All attendees were fetched already. Nothing to do.")
            return

    LOGGER.info("Will now fetch %s." % ", ".join(["%s"] * len(attendees)), *map(hl, attendees))

    for attendee in attendees:
        attendee.fetch(force=force)

    LOGGER.info("Done fetching %s attendee(s)...", hl(len(attendees)))


def unpack(attendees=None, force=False):
    """
    Unpack the specified attendees.
    """

    fetch(attendees, force=False)

    attendees = Attendee.get_dependent_instances(attendees or None)

    if force:
        LOGGER.info("Force unpack requested...")
    else:
        attendees = [x for x in attendees if x.must_unpack]

        if not attendees:
            LOGGER.info("All attendees were unpacked already. Nothing to do.")
            return

    LOGGER.info("Will now unpack %s." % ", ".join(["%s"] * len(attendees)), *map(hl, attendees))

    for attendee in attendees:
        attendee.unpack(force=force)

    LOGGER.info("Done unpacking %s attendee(s)...", hl(len(attendees)))


def build(attendees=None, force=False, verbose=False, keep_builds=False):
    """
    Build the specified attendees.
    """

    unpack(attendees, force=False)

    attendees = Attendee.get_dependent_instances(attendees or None)

    if force:
        LOGGER.info("Force build requested...")
    else:
        attendees = [x for x in attendees if x.must_build]

        if not attendees:
            LOGGER.info("All attendees were built already. Nothing to do.")
            return

    LOGGER.info("Will now build %s." % ", ".join(["%s"] * len(attendees)), *map(hl, attendees))

    for attendee in attendees:
        attendee.build(force=force, verbose=verbose, keep_builds=keep_builds)

    LOGGER.info("Done building %s attendee(s)...", hl(len(attendees)))
