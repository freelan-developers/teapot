"""
A Github fetcher class.
"""

import re

from teapot.fetchers.fetcher import register_fetcher
from teapot.fetchers.http_fetcher import HttpFetcher


@register_fetcher('github')
class GithubFetcher(HttpFetcher):

    """
    Fetchs an archive from Github.
    """

    def parse_source(self, source):
        """
        Checks that the `source` is a local filename.
        """

        match = re.match(r'github:(?P<owner>[\S/]+)/(?P<repo>[\S/]+)/(?P<ref>.+)', source.resource)

        if match:
            values = match.groupdict()
            values['archive_format'] = 'tarball'

            return {
                'url': 'https://api.github.com/repos/%(owner)s/%(repo)s/%(archive_format)s/%(ref)s' % values,
                'mimetype': source.mimetype,
            }
