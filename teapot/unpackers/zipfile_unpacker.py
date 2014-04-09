"""
An unpacker that deals with .zip files.
"""

from teapot.unpackers.unpacker import UnpackerImplementation
from teapot.unpackers.unpacker import register_unpacker

from ..error import TeapotError
from ..log import Highlight as hl

import os
import zipfile


@register_unpacker(('application/zip', None))
class ZipFileUnpacker(UnpackerImplementation):

    """
    An unpacker class that deals with .zip files.
    """

    def unpack(self, archive_path, target_path, progress):
        """
        Uncompress the archive.
        """

        if not zipfile.is_zipfile(archive_path):
            raise TeapotError(
                "%s is not a valid zip archive.",
                hl(archive_path),
            )

        zipf = zipfile.ZipFile(archive_path, 'r')

        # We get the common prefix for all archive members.
        prefix = os.path.commonprefix(zipf.namelist())

        while prefix and not prefix.endswith('/'):
            prefix = os.path.dirname(prefix)

        # We remove the trailing '/'
        prefix = os.path.dirname(prefix)

        if not prefix:
            raise TeapotError(
                "Unable to find a common prefix in %s to extract from.",
                hl(archive_path),
            )

        extracted_sources_path = os.path.join(target_path, prefix)

        progress.on_start(archive_path=archive_path, count=len(zipf.infolist()))

        for index, info in enumerate(zipf.infolist()):
            if os.path.isabs(info.filename):
                raise ValueError('Refusing to extract archive that contains absolute filenames.')

            progress.on_update(current_file=info.filename, progress=index)
            zipf.extract(info, path=target_path)

        progress.on_finish()

        return {
            'extracted_sources_path': extracted_sources_path,
        }
