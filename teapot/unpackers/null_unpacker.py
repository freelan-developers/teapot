"""
An unpacker that does nothing.
"""

from teapot.unpackers.unpacker import UnpackerImplementation
from teapot.unpackers.unpacker import register_unpacker

from ..error import TeapotError
from ..log import Highlight as hl

import os
import shutil


@register_unpacker((None, None))
class NullUnpacker(UnpackerImplementation):

    """
    An unpacker class that just copy source trees.
    """

    def unpack(self, archive_path, target_path, progress):
        """
        Uncompress the archive.

        Return the path of the extracted folder.
        """

        if not os.path.isdir(archive_path):
            raise ValueError('A directory was expected.')

        extracted_sources_path = os.path.join(target_path, os.path.basename(archive_path))

        progress.on_start(archive_path=archive_path, count=1)

        progress.on_update(current_file=archive_path, progress=1)
        shutil.copytree(archive_path, extracted_sources_path)

        progress.on_finish()

        return {
            'extracted_sources_path': extracted_sources_path,
        }
