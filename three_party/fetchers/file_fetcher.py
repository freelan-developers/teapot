"""
A local-file fetcher class.
"""

from three_party.fetchers.base_fetcher import BaseFetcher


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

    def fetch(self, location):
        """
        Fetch the filename at the specified location.
        """

        # TODO: Implement
        print 'Copying file at %s' % location
