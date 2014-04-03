"""
The party classes.
"""

import os
import imp

from .log import LOGGER


def load_party_file(path):
    """
    Load a Party from a file.

    `path` must point to an existing party file.
    """

    path = os.path.abspath(path)

    LOGGER.debug('Importing party file from %r', path)
    imp.load_source('party', path)


def fetch(attendees=None, force=False):
    """
    Fetches the specified attendees.
    """

    pass
