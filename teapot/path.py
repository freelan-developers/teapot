"""
A teapot path-handling class.
"""

import os
import stat
import shutil
import errno

from contextlib import contextmanager

from teapot.log import LOGGER
from teapot.log import Highlight as hl


def from_user_path(path):
    """
    Perform all variables substitutions from the specified user path.
    """

    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))


def read_path(value, base_path, default_path):
    """
    Read a path value from a string.

    If `value` is a string, the Cache is default created at the location
    specified by `value`.

    If `value` is falsy, the Cache is default created.
    """

    if not value:
        cache_path = from_user_path(default_path)
    else:
        cache_path = from_user_path(value)

    if not os.path.isabs(cache_path):
        cache_path = os.path.normpath(os.path.join(base_path, cache_path))

    return cache_path


@contextmanager
def chdir(path):
    """
    Changes the directory temporarily.
    """

    path = os.path.abspath(path)
    saved_dir = os.getcwd()

    if os.path.abspath(saved_dir) != os.path.abspath(path):
        LOGGER.debug(
            "Temporarily changing current directory from %s to %s",
            hl(saved_dir),
            hl(path),
        )

        os.chdir(path)

    try:
        yield
    finally:
        if os.path.abspath(saved_dir) != os.path.abspath(path):
            LOGGER.debug(
                "Changing back current directory from %s to %s",
                hl(path),
                hl(saved_dir),
            )

            os.chdir(saved_dir)


def mkdir(path):
    """
    Create the specified path.

    Does nothing if the path exists.
    """

    try:
        if not os.path.isdir(path):
            LOGGER.debug('Creating directory at %s.', hl(path))

        os.makedirs(path)

    except OSError as ex:
        if ex.errno != errno.EEXIST or not os.path.isdir(path):
            raise


def rmdir(path):
    """
    Delete the specified path if it exists.

    Does nothing if the path doesn't exist.
    """

    try:
        LOGGER.debug('Removing directory at %s.', hl(path))

        def onerror(func, path, excinfo):
            if os.path.exists(path):
                LOGGER.debug('Was unable to delete "%s": %s', hl(path), excinfo[1])
                LOGGER.debug('Trying again after changing permissions...')
                os.chmod(path, stat.S_IWUSR)

                try:
                    func(path)
                except Exception as ex:
                    LOGGER.error('Unable to delete "%s": %s', hl(path), excinfo[1])

                    raise

        shutil.rmtree(path, ignore_errors=False, onerror=onerror)

    except Exception as ex:
        LOGGER.debug(ex)


def windows_to_unix_path(path):
    """
    Convert a Windows path to a UNIX path, in such a way that it can be used in
    MSys or Cygwin.
    """

    drive, tail = os.path.splitdrive(path)

    if drive:
        drive = '/' + drive[0]

    return drive + tail.replace('\\', '/')
