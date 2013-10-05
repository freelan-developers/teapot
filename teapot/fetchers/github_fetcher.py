"""
A Github fetcher class.
"""

import re

from teapot.fetchers.http_fetcher import HttpFetcher


class GithubFetcher(HttpFetcher):

    """
    Fetchs an archive from Github.
    """

    shortname = 'github'

    def read_source(self, source):
        """
        Checks that the `source` is a Github URL.
        """

        assert(source)

        match = re.match(r'github:(?P<owner>[\S/]+)/(?P<repo>[\S/]+)/(?P<ref>.+)', source.location)

        if match:
            values = match.groupdict()
            values['archive_format'] = 'tarball'

            self.url = 'https://api.github.com/repos/%(owner)s/%(repo)s/%(archive_format)s/%(ref)s' % values

            return True
