"""
An unpacker that deals with .tgz files.
"""

from tea_party.unpackers.base_unpacker import BaseUnpacker, UnsupportedArchiveError

import os
import tarfile

class TarballUnpacker(BaseUnpacker):

    """
    An unpacker class that deals with .tgz files.
    """

    types = [
        ('application/x-gzip', None),
    ]

    def unpack(self):
        """
        Uncompress the archive.

        Return the path of the extracted folder.
        """

        if not tarfile.is_tarfile(archive_path):
            raise UnsupportedArchiveError(archive_path=archive_path)

        extract_path = os.path.dirname(archive_path)

        tar = tarfile.open(archive_path, 'r')

        tar.list(True)

        return extract_path
