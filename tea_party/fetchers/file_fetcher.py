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

        target_file_path = os.path.join(target, os.path.basename(location))

        shutil.copyfile(location, target_file_path)

        return target_file_path
