"""
A HTTP fetcher class.
"""

import os
import urlparse
import requests
import shutil
import mimetypes
from rfc6266 import parse_requests_response

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

    def do_fetch(self, target):
        """
        Fetch the archive at the specified location.
        """

        response = requests.get(self.location, stream=True)
        response.raise_for_status()

        mimetype = response.headers.get('content-type')

        extension = mimetypes.guess_extension(mimetype)
        content_disposition = parse_requests_response(response)

        filename = content_disposition.filename_sanitized(extension=extension[1:], default_filename='archive')

        content_length = response.headers.get('content-length')

        if content_length is not None:
            content_length = int(content_length)

        target_file_path = os.path.join(target, filename)

        self.on_start(target=os.path.basename(target_file_path), size=content_length)

        with open(target_file_path, 'wb') as target_file:
            current_size = 0

            for buf in response.iter_content(1024):

                if buf:
                    target_file.write(buf)
                    current_size += len(buf)

                    self.on_update(progress=current_size)

        self.on_finish()

        return target_file_path, mimetype
