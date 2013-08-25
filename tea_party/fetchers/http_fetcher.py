"""
A HTTP fetcher class.
"""

import os
import urlparse
import requests
import shutil
import mimetypes
from rfc6266 import parse_requests_response

from tea_party.log import LOGGER
from tea_party.fetchers.base_fetcher import BaseFetcher


class HttpFetcher(BaseFetcher):

    """
    Fetchs a file from the web, using HTTP or HTTPS.
    """

    shortname = 'http'

    def read_source(self, source):
        """
        Checks that the `source` is an HTTP(S) URL.
        """

        assert(source)

        url = urlparse.urlparse(source.location)

        if url.scheme in ['http', 'https']:
            self.url = urlparse.urlunparse(url)

            return True

    def do_fetch(self, target):
        """
        Fetch the archive at the specified URL.
        """

        response = requests.get(self.url, stream=True)
        response.raise_for_status()

        mimetype = response.headers.get('content-type')
        encoding = response.headers.get('content-encoding')
        archive_type = (mimetype, encoding)

        # If the source has an overriden type, we use that instead.
        if self.source._type:
            extension = mimetypes.guess_extension(self.source._type[0])

        if not extension:
            extension = mimetypes.guess_extension(mimetype)

        if not extension:
            LOGGER.debug('No extension registered for this mimetype (%s). Guessing one from the URL...', mimetype)

            extension = os.path.splitext(urlparse.urlparse(self.url).path)[1]

        if extension and extension.startswith('.'):
            extension = extension[1:]

        content_disposition = parse_requests_response(response)

        filename = content_disposition.filename_sanitized(extension=extension, default_filename='archive')

        content_length = response.headers.get('content-length')

        if content_length is not None:
            content_length = int(content_length)

        archive_path = os.path.join(target, filename)

        self.progress.on_start(target=os.path.basename(archive_path), size=content_length)

        with open(archive_path, 'wb') as target_file:
            current_size = 0

            for buf in response.iter_content(1024):

                if buf:
                    target_file.write(buf)
                    current_size += len(buf)

                    self.progress.on_update(progress=current_size)

        self.progress.on_finish()

        return {
            'archive_path': archive_path,
            'archive_type': archive_type,
        }
