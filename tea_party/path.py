"""
A tea-party path-handling class.
"""

import os


def from_user_path(path):
    """
    Perform all variables substitutions from the specified user path.
    """

    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))
