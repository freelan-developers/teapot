"""
A tea-party cache class.
"""

import os
import errno
import shutil

from tea_party.log import LOGGER
from tea_party.path import from_user_path
from tea_party.defaults import *


def make_cache(data, base_path):
    """
    Make a Cache instance from a string or dictionary.

    If `data` is a string, the Cache is default created at the location
    specified by `data.

    If `data` is a dictionary, it contains the attributes for the Cache
    instance to create.

    If `data` is falsy, the Cache is default created.
    """

    if not data:
        cache_path = from_user_path(DEFAULT_CACHE_PATH)
    elif isinstance(data, basestring):
        cache_path = from_user_path(data)
    else:
        cache_path = from_user_path(data.get('location', DEFAULT_CACHE_PATH))

    if not os.path.isabs(cache_path):
        cache_path = os.path.normpath(os.path.join(base_path, cache_path))

    return Cache(path=cache_path)

class Cache(object):

    """
    A Cache instance holds information about the fetched archives.
    """

    def __init__(self, path):
        """
        Create a Cache instance.

        `path` is the cache root directory.
        """

        self.path = os.path.abspath(path)

        try:
            os.makedirs(self.path)

            LOGGER.info('Creating cache directory: %s', self.path)

        except OSError as ex:
            if ex.errno == errno.EEXIST and os.path.isdir(self.path):
                LOGGER.debug('Cache directory is at: %s', self.path)
            else:
                raise

    def clean(self):
        """
        Erases completely the cache directory.
        """

        try:
            LOGGER.debug('Cleaning cache at %s', self.path)

            shutil.rmtree(self.path)

        except Exception as ex:
            LOGGER.debug(ex)

    def get_attendee_directory(self, attendee):
        """
        Get an attendee directory.

        The directory is not guaranteed to exist.
        """

        return os.path.join(self.path, unicode(attendee))

    def clean_attendee_directory(self, attendee):
        """
        Clean an attendee directory.
        """

        path = self.get_attendee_directory(attendee)

        try:
            LOGGER.debug('Cleaning %s\'s directory at %s', attendee, path)

            shutil.rmtree(path)

        except Exception as ex:
            LOGGER.debug(ex)

    def get_attendee_cache_directory(self, attendee):
        """
        Get the attendee cache directory.
        """

        return os.path.join(self.get_attendee_directory(attendee), 'cache')

    def create_attendee_cache_directory(self, attendee):
        """
        Create the attendee cache directory.
        """

        path = self.get_attendee_cache_directory(attendee)

        try:
            LOGGER.debug('Creating %s\'s cache directory at %s.', attendee, path)

            os.makedirs(path)

        except OSError as ex:
            if ex.errno != errno.EEXIST or not os.path.isdir(path):
                raise

        return path

    def clean_attendee_cache_directory(self, attendee):
        """
        Clean the attendee cache directory.
        """

        path = self.get_attendee_cache_directory(attendee)

        try:
            LOGGER.debug('Destroying %s\'s cache directory at %s.', attendee, path)

            shutil.rmtree(path)

        except Exception as ex:
            LOGGER.debug(ex)

    def get_attendee_build_directory(self, attendee):
        """
        Get the attendee build directory.
        """

        return os.path.join(self.get_attendee_directory(attendee), 'build')

    def create_attendee_build_directory(self, attendee):
        """
        Create the attendee build directory.
        """

        path = self.get_attendee_build_directory(attendee)

        try:
            LOGGER.debug('Creating %s\'s build directory at %s.', attendee, path)

            os.makedirs(path)

        except OSError as ex:
            if ex.errno != errno.EEXIST or not os.path.isdir(path):
                raise

        return path

    def clean_attendee_build_directory(self, attendee):
        """
        Clean the attendee build directory.
        """

        path = self.get_attendee_build_directory(attendee)

        try:
            LOGGER.debug('Destroying %s\'s build directory at %s.', attendee, path)

            shutil.rmtree(path)

        except Exception as ex:
            LOGGER.debug(ex)
