"""
An unpacker that deals with .zip files.
"""

from tea_party.unpackers.base_unpacker import BaseUnpacker

import os
import zipfile

class InvalidZipFileError(RuntimeError):

    """
    The specified archive is not a supported zip file.
    """

    def __init__(self, archive_path):
        """
        Create an InvalidZipFileError for the specified `archive_path`.
        """

        super(InvalidZipFileError, self).__init__(
            'Unsupported archive: %s' % archive_path
        )


class ZipFileHasNoCommonPrefixError(RuntimeError):

    """
    The specified archive does not contain a common prefix for its members.
    """

    def __init__(self, archive_path):
        """
        Create an ZipFileHasNoCommonPrefixError for the specified
        `archive_path`.
        """

        super(ZipFileHasNoCommonPrefixError, self).__init__(
            'The specified archive contains no common prefix: %s' % archive_path
        )


class ZipFileUnpacker(BaseUnpacker):

    """
    An unpacker class that deals with .zip files.
    """

    types = [
        ('application/zip', None),
    ]

    def do_unpack(self):
        """
        Uncompress the archive.

        Return the path of the extracted folder.
        """

        if not zipfile.is_zipfile(self.archive_path):
            raise InvalidZipFileError(archive_path=self.archive_path)

        zipf = zipfile.ZipFile(self.archive_path, 'r')

        # We get the common prefix for all archive members.
        prefix = os.path.commonprefix(zipf.namelist())

        while prefix and not prefix.endswith('/'):
            prefix = os.path.dirname(prefix)

        # We remove the trailing '/'
        prefix = os.path.dirname(prefix)

        if not prefix:
            raise ZipFileHasNoCommonPrefixError(archive_path=self.archive_path)

        source_tree_path = os.path.join(self.attendee.build_path, prefix)

        self.progress.on_start(count=len(zipf.infolist()))

        for index, info in enumerate(zipf.infolist()):
            if os.path.isabs(info.filename):
                raise ValueError('Refusing to extract archive that contains absolute filenames.')

            self.progress.on_update(current_file=info.filename, progress=index)
            zipf.extract(info, path=self.attendee.build_path)

        self.progress.on_finish()

        return {
            'source_tree_path': source_tree_path,
        }
