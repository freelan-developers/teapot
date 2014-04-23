"""
A teapot path-handling class.
"""

import os
import stat
import shutil
import errno

from contextlib import contextmanager
from functools import wraps

from teapot.log import LOGGER
from teapot.log import Highlight as hl


def from_user_path(path):
    """
    Perform all variables substitutions from the specified user path.
    """

    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))


def resolve_user_path(func):
    """
    A decorator that resolves user paths in the return value.
    """

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        return from_user_path(func(*args, **kwargs))

    return wrapped_func


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
        LOGGER.info('Removing directory at %s.', hl(path))

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
        LOGGER.warning(ex)


def copytree(src, dst, symlinks=False, ignore=None, copy_function=shutil.copy2):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore, copy_function)
            else:
                try:
                    copy_function(srcname, dstname)
                except (IOError, WindowsError):
                    shutil.copy2(srcname, dstname)

            # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)


@contextmanager
def temporary_copy(source_path, target_path, persistent=False):
    """
    Copy a source path to a target path.

    The target will be deleted upon function exist, unless `persistent`
    is truthy.
    """

    try:
        if os.path.exists(target_path):
            rmdir(target_path)

        LOGGER.info('Copying %s to %s...', hl(source_path), hl(target_path))
        copytree(source_path, target_path, copy_function=getattr(os, 'link', shutil.copy2))

        yield target_path

    finally:
        if not persistent:
            rmdir(target_path)
        else:
            LOGGER.info('Not erasing temporary directory at %s.', hl(target_path))


def windows_to_unix_path(path):
    """
    Convert a Windows path to a UNIX path, in such a way that it can be used in
    MSys or Cygwin.
    """

    drive, tail = os.path.splitdrive(path)

    if drive:
        drive = '/' + drive[0]

    return drive + tail.replace('\\', '/')


@contextmanager
def chdir(path):
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
