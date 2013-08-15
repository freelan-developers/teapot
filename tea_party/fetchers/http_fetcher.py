"""
A HTTP fetcher class.
"""

import urlparse
import requests
import shutil

from tea_party.fetchers.base_fetcher import BaseFetcher


class HttpFetcher(BaseFetcher):

    """
    Fetchs a file from the web, using HTTP or HTTPS.
    """

    shortname = 'http'

    def normalize_location(self, location):
        """
        Checks that the `location` is an HTTP(S) URL.
        """

        url = urlparse.urlparse(location)

        if url.scheme in ['http', 'https']:
            return urlparse.urlunparse(url)

    def fetch(self, location, target):
        """
        Fetch the archive at the specified location.
        """

        response = requests.get(location, stream=True)
        response.raise_for_status()

        if 'content-disposition' in response.headers:
            print response.headers['content-disposition']

        with open(target, 'wb') as target_file:
            shutil.copyfileobj(response.raw, target_file)

        return target
