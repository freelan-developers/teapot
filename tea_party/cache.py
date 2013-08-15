"""
A tea-party cache class.
"""

import os
import errno
from tea_party.log import LOGGER


def make_cache(data, base_path):
    """
    Make a Cache instance from a string or dictionary.

    If `data` is a string, the Cache is default created at the location
    specified by `data.

    If `data` is a dictionary, it contains the attributes for the Cache
    instance to create.

    If `data` is falsy, the Cache is default created.
    """

    DEFAULT_NAME = '.party-cache'

    if not data:
        return Cache(path=os.path.relpath(os.path.join(base_path, DEFAULT_NAME), os.getcwd()))
    elif isinstance(data, basestring):
        return Cache(path=os.path.relpath(os.path.join(base_path, data), os.getcwd()))
    else:
        return Cache(path=os.path.relpath(os.path.join(base_path, data.get('location', DEFAULT_NAME)), os.getcwd()))

class Cache(object):

    """
    A Cache instance holds information about the fetched archives.
    """

    def __init__(self, path):
        """
        Create a Cache instance.

        `path` is the cache root directory.
        """

        self.path = path

        try:
            os.makedirs(self.path)

            LOGGER.info('Creating cache directory: %s', self.path)

        except OSError as ex:
            if ex.errno == errno.EEXIST and os.path.isdir(self.path):
                LOGGER.debug('Cache directory is at: %s', self.path)
            else:
                raise
