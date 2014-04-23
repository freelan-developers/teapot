"""
A HTTP fetcher class.
"""

import os
import urlparse
import requests
import shutil
import mimetypes

from teapot.extra.rfc6266 import parse_requests_response

from teapot.fetchers.fetcher import register_fetcher
from teapot.fetchers.fetcher import FetcherImplementation
from teapot.path import rmdir
from teapot.log import LOGGER


@register_fetcher('http')
class HttpFetcher(FetcherImplementation):

    """
    Fetchs a file on the local filesystem.
    """

    def parse_source(self, source):
        """
        Checks that the `source` is a local filename.
        """

        url = urlparse.urlparse(source.resource)

        if url.scheme in ['http', 'https']:
            return {
                'url': urlparse.urlunparse(url),
                'mimetype': source.mimetype,
            }

    def fetch(self, fetch_info, target_path, progress):
        """
        Fetch a file.
        """

        response = requests.get(fetch_info['url'], stream=True)
        response.raise_for_status()

        mimetype = fetch_info['mimetype'] or response.headers.get('content-type')
        encoding = response.headers.get('content-encoding')
        archive_type = (mimetype, encoding)

        # If the source has an overriden type, we use that instead.
        extension = None

        if fetch_info['mimetype']:
            extension = mimetypes.guess_extension(fetch_info['mimetype'])

        if not extension:
            extension = mimetypes.guess_extension(mimetype)

        if not extension:
            LOGGER.debug('No extension registered for this mimetype (%s). Guessing one from the URL...', mimetype)

            extension = os.path.splitext(urlparse.urlparse(fetch_info['url']).path)[1]

        if extension and extension.startswith('.'):
            extension = extension[1:]

        content_disposition = parse_requests_response(response)

        filename = content_disposition.filename_sanitized(extension=extension, default_filename='archive')

        content_length = response.headers.get('content-length')

        if content_length is not None:
            content_length = int(content_length)

        archive_path = os.path.join(target_path, filename)

        progress.on_start(target=os.path.basename(archive_path), size=content_length)

        with open(archive_path, 'wb') as target_file:
            current_size = 0

            for buf in response.iter_content(1024):

                if buf:
                    target_file.write(buf)
                    current_size += len(buf)

                    progress.on_update(progress=current_size)

        progress.on_finish()

        return {
            'archive_path': archive_path,
            'archive_type': archive_type,
        }
