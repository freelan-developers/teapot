"""
A local-folder fetcher class.
"""

import os
import shutil
import urlparse

from teapot.fetchers.fetcher import register_fetcher
from teapot.fetchers.fetcher import FetcherImplementation
from teapot.path import rmdir


@register_fetcher('folder')
class FolderFetcher(FetcherImplementation):

    """
    Fetchs a folder on the local filesystem.
    """

    def parse_source(self, source):
        """
        Checks that the `source` is a local filename.
        """

        parse = urlparse.urlsplit(source.resource)

        if parse.scheme == 'folder':
            return {
                'folder_path': os.path.abspath(parse.netloc + parse.path),
            }

    def fetch(self, fetch_info, target_path, progress):
        """
        Fetch a folder.
        """

        archive_path = os.path.join(target_path, os.path.basename(fetch_info['folder_path']))

        rmdir(archive_path)

        progress.on_start(target=os.path.basename(archive_path), size=None)

        if os.path.isdir(fetch_info['folder_path']):
            shutil.copytree(fetch_info['folder_path'], archive_path)
            archive_type = (None, None)

        # No real interactive progress to show here.
        #
        # This could be fixed though.

        progress.on_update(progress=None)
        progress.on_finish()

        return {
            'archive_path': archive_path,
            'archive_type': archive_type,
        }
