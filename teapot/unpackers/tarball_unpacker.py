"""
An unpacker that deals with .tgz files.
"""

from teapot.unpackers.base_unpacker import BaseUnpacker

import os
import tarfile

class InvalidTarballError(RuntimeError):

    """
    The specified archive is not a supported tarball.
    """

    def __init__(self, archive_path):
        """
        Create an InvalidTarballError for the specified `archive_path`.
        """

        super(InvalidTarballError, self).__init__(
            'Unsupported archive: %s' % archive_path
        )


class TarballHasNoCommonPrefixError(RuntimeError):

    """
    The specified archive does not contain a common prefix for its members.
    """

    def __init__(self, archive_path):
        """
        Create an TarballHasNoCommonPrefixError for the specified
        `archive_path`.
        """

        super(TarballHasNoCommonPrefixError, self).__init__(
            'The specified archive contains no common prefix: %s' % archive_path
        )


class TarballUnpacker(BaseUnpacker):

    """
    An unpacker class that deals with .tgz files.
    """

    types = [
        ('application/x-gzip', None),
        ('application/x-bzip2', None),
    ]

    def do_unpack(self):
        """
        Uncompress the archive.

        Return the path of the extracted folder.
        """

        if not tarfile.is_tarfile(self.archive_path):
            raise InvalidTarballError(archive_path=self.archive_path)

        tar = tarfile.open(self.archive_path, 'r')

        # We get the common prefix for all archive members.
        prefix = os.path.commonprefix(tar.getnames())

        # An archive member with the prefix as a name should exist in the archive.
        while True:
            try:
                prefix_member = tar.getmember(prefix)

                if prefix_member.isdir:
                    break

            except KeyError:
                pass

            new_prefix = os.path.dirname(prefix)

            if prefix == new_prefix:
                raise TarballHasNoCommonPrefixError(archive_path=self.archive_path)
            else:
                prefix = new_prefix

        source_tree_path = os.path.join(self.attendee.build_path, prefix_member.name)

        self.progress.on_start(count=len(tar.getmembers()))

        for index, member in enumerate(tar.getmembers()):
            if os.path.isabs(member.name):
                raise ValueError('Refusing to extract archive that contains absolute filenames.')

            self.progress.on_update(current_file=member.name, progress=index)
            tar.extract(member, path=self.attendee.build_path)

        self.progress.on_finish()

        return {
            'source_tree_path': source_tree_path,
        }
