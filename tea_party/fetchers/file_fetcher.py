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

    def read_source(self, source):
        """
        Checks that the `source` is a local filename.
        """

        if os.path.isfile(source.location):
            self.file_path = os.path.abspath(source.location)

            return True

    def do_fetch(self, target):
        """
        Fetch a filename.
        """

        archive_path = os.path.join(target, os.path.basename(self.file_path))

        archive_type = mimetypes.guess_type(self.file_path)
        size = os.path.getsize(self.file_path)

        self.progress.on_start(target=os.path.basename(archive_path), size=size)

        shutil.copyfile(self.file_path, archive_path)

        self.progress.on_update(progress=size)
        self.progress.on_finish()

        return {
            'archive_path': archive_path,
            'archive_type': archive_type,
        }
