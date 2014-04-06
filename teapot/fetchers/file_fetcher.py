"""
A local-file fetcher class.
"""

import os
import shutil
import mimetypes

from teapot.fetchers.fetcher import register_fetcher
from teapot.fetchers.fetcher import FetcherImplementation
from teapot.path import rmdir


@register_fetcher('file')
class FileFetcher(FetcherImplementation):

    """
    Fetchs a file on the local filesystem.
    """

    def parse_source(self, source):
        """
        Checks that the `source` is a local filename.
        """

        if os.path.exists(source.resource):
            return {
                'file_path': os.path.abspath(source.resource),
            }

    def fetch(self, parsed_source, target_path, progress):
        """
        Fetch a file.
        """

        archive_path = os.path.join(target_path, os.path.basename(self.file_path))

        size = os.path.getsize(self.file_path)

        if not size:
            size = None

        rmdir(archive_path)

        progress.on_start(target=os.path.basename(archive_path), size=size)

        if os.path.isfile(self.file_path):
            shutil.copyfile(self.file_path, archive_path)
            archive_type = mimetypes.guess_type(self.file_path, strict=False)
        elif os.path.isdir(self.file_path):
            shutil.copytree(self.file_path, archive_path)
            archive_type = (None, None)

        # No real interactive progress to show here.
        #
        # This could be fixed though.

        progress.on_update(progress=size)
        progress.on_finish()

        return archive_path, archive_type
