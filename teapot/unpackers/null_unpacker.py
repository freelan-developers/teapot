"""
An unpacker that does nothing.
"""

from teapot.unpackers.base_unpacker import BaseUnpacker

import os
import shutil


class NullUnpacker(BaseUnpacker):

    """
    An unpacker class that just copy source trees.
    """

    types = [
        (None, None),
    ]

    def do_unpack(self):
        """
        Uncompress the archive.

        Return the path of the extracted folder.
        """

        if not os.path.isdir(self.archive_path):
            raise RuntimeError('A directory was expected.')

        source_tree_path = os.path.join(self.attendee.build_path, os.path.basename(self.archive_path))

        self.progress.on_start(count=1)

        self.progress.on_update(current_file=self.archive_path, progress=1)
        shutil.copytree(self.archive_path, source_tree_path)

        self.progress.on_finish()

        return {
            'source_tree_path': source_tree_path,
        }
