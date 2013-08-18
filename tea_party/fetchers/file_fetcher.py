"""
A local-file fetcher class.
"""

import os
import shutil
import mimetypes

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

    def do_fetch(self, target):
        """
        Fetch the filename at the specified location.
        """

        target_file_path = os.path.join(target, os.path.basename(self.location))

        mimetype = mimetypes.guess_type(self.location)[0]
        size = os.path.getsize(self.location)

        self.on_start(target=os.path.basename(target_file_path), size=size)

        shutil.copyfile(self.location, target_file_path)

        self.on_update(progress=size)
        self.on_finish()

        return target_file_path, mimetype
