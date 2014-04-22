"""
A local-file fetcher class.
"""

import os
import shutil
import urlparse
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

        parse = urlparse.urlsplit(source.resource)

        if parse.scheme == 'file':
            return {
                'file_path': os.path.abspath(parse.netloc + parse.path),
            }

    def fetch(self, fetch_info, target_path, progress):
        """
        Fetch a file.
        """

        archive_path = os.path.join(target_path, os.path.basename(fetch_info['file_path']))

        size = os.path.getsize(fetch_info['file_path'])

        if not size:
            size = None

        rmdir(archive_path)

        progress.on_start(target=os.path.basename(archive_path), size=size)

        if os.path.isfile(fetch_info['file_path']):
            shutil.copyfile(fetch_info['file_path'], archive_path)
            archive_type = mimetypes.guess_type(fetch_info['file_path'], strict=False)

        # No real interactive progress to show here.
        #
        # This could be fixed though.

        progress.on_update(progress=size)
        progress.on_finish()

        return {
            'archive_path': archive_path,
            'archive_type': archive_type,
        }
