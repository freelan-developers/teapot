"""
An unpacker that deals with .tgz files.
"""

from teapot.unpackers.unpacker import UnpackerImplementation
from teapot.unpackers.unpacker import register_unpacker

from ..error import TeapotError
from ..log import Highlight as hl

import os
import tarfile


@register_unpacker(('application/x-gzip', None))
@register_unpacker(('application/x-bzip2', None))
class TarballUnpacker(UnpackerImplementation):

    """
    An unpacker class that deals with .tgz files.
    """

    def unpack(self, archive_path, target_path, progress):
        """
        Uncompress the archive.
        """

        if not tarfile.is_tarfile(archive_path):
            raise TeapotError(
                "%s is not a valid tar archive.",
                hl(archive_path),
            )

        tar = tarfile.open(archive_path, 'r')

        # We get the common prefix for all archive members.
        prefix = os.path.commonprefix(tar.getnames())

        # An archive member with the prefix as a name can exist in the archive or ends with a /.
        while not prefix.endswith('/'):
            try:
                prefix_member = tar.getmember(prefix)

                if prefix_member.isdir:
                    break

            except KeyError:
                pass

            new_prefix = os.path.dirname(prefix)

            if prefix == new_prefix:
                raise TeapotError(
                    "Unable to find a common prefix in %s to extract from.",
                    hl(archive_path),
                )
            else:
                prefix = new_prefix

        extracted_sources_path = os.path.join(target_path, prefix)

        progress.on_start(archive_path=archive_path, count=len(tar.getmembers()))

        for index, member in enumerate(tar.getmembers()):
            if os.path.isabs(member.name):
                raise TeapotError(
                    (
                        "Refusing to extract an archive (%s) that contains "
                        "absolute filenames."
                    ),
                    hl(archive_path),
                )

            progress.on_update(current_file=member.name, progress=index)
            tar.extract(member, path=target_path)

        progress.on_finish()

        return {
            'extracted_sources_path': extracted_sources_path,
        }
