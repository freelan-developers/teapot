"""
A local-file fetcher class.
"""

import os
import shutil
import mimetypes

from teapot.fetchers.base_fetcher import BaseFetcher
from teapot.path import rmdir


class FileFetcher(BaseFetcher):

    """
    Fetchs a file on the local filesystem.
    """

    shortname = 'file'

    def read_source(self, source):
        """
        Checks that the `source` is a local filename.
        """

        if os.path.exists(source.location):
            self.file_path = os.path.abspath(source.location)

            return True

    def do_fetch(self, target):
        """
        Fetch a filename.
        """

        archive_path = os.path.join(target, os.path.basename(self.file_path))

        archive_type = mimetypes.guess_type(self.file_path)
        size = os.path.getsize(self.file_path)

        rmdir(archive_path)

        self.progress.on_start(target=os.path.basename(archive_path), size=size)

        if os.path.isfile(self.file_path):
            shutil.copyfile(self.file_path, archive_path)
        elif os.path.isdir(self.file_path):
            shutil.copytree(self.file_path, archive_path)
        else:
            raise RuntimeError('Unsupported path: %s' % self.file_path)

        # No real interactive progress to show here.
        #
        # This could be fixed though.

        self.progress.on_update(progress=size)
        self.progress.on_finish()

        return {
            'archive_path': archive_path,
            'archive_type': archive_type,
        }
