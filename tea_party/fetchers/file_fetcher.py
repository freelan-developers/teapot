"""
A local-file fetcher class.
"""

import os
import shutil

from tea_party.fetchers.base_fetcher import BaseFetcher


class FileFetcher(BaseFetcher):

    """
    Fetchs a file on the local filesystem.
    """

    shortname = 'file'

    def normalize_location(self, location):
        """
        Checks that the `location` is a local filename.
        """

        if os.path.isfile(location):
            return os.path.abspath(location)

    def fetch(self, location, target):
        """
        Fetch the filename at the specified location.
        """

        # We are given a filename, but we want to keep the original.
        target = os.path.join(os.path.dirname(target), os.path.basename(location))

        shutil.copyfile(location, target)

        return target
