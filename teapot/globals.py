"""
Some global variables.
"""

import os

from contextlib import contextmanager


GLOBALS = {
    'PARTY_PATH': None,
}


@contextmanager
def set_party_path(path):
    old_party_path, GLOBALS['PARTY_PATH'] = GLOBALS['PARTY_PATH'], os.path.abspath(path)

    try:
        yield
    finally:
        GLOBALS['PARTY_PATH'] = old_party_path


def get_party_path():
    return GLOBALS['PARTY_PATH']
