"""
Some test fetchers.
"""

import os

from teapot.fetchers.base_fetcher import BaseFetcher



class FooFetcher(BaseFetcher):

    """
    Simulates a successful fetch.
    """

    shortname = 'foo'

    def read_source(self, source):
        """
        Checks that the `source` is a local filename.
        """

        if source.location.startswith('foo://'):
            self.resource = source.location[len('foo://'):]

            return True

    def do_fetch(self, target):
        """
        Simulates the fetch.
        """

        archive_path = os.path.join(target, self.resource)
        archive_type = 'application/foo-archive'

        size = 100

        self.progress.on_start(target=os.path.basename(archive_path), size=size)
        self.progress.on_update(progress=size)
        self.progress.on_finish()

        return {
            'archive_path': archive_path,
            'archive_type': archive_type,
        }
