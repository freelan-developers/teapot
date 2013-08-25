"""
Contains all tea-party unpackers logic.

If you want to create your own unpacker, derive from
tea_party.unpackers.base_unpacker.BaseUnpacker.
"""

from tea_party.unpackers.base_unpacker import BaseUnpacker
from tea_party.unpackers.tarball_unpacker import TarballUnpacker
from tea_party.unpackers.zipfile_unpacker import ZipFileUnpacker


class NoSuchUnpackerError(ValueError):

    """
    Raised when a non-existing unpacker was requested.
    """

    def __init__(self, _type):
        """
        Create a NoSuchUnpackerError instance for the specified `_type`.
        """

        super(
            NoSuchUnpackerError,
            self
        ).__init__(
            'No suitable unpacker found for: %s' % repr(_type)
        )


def get_unpacker_class_for_type(_type):
    """
    Get the appropriate unpacker class/builder for a given `_type`.

    If no unpacker supports `_type` a NoSuchUnpackerError instance is
    raised.
    """

    if not _type:
        raise ValueError('Unable to get an unpacker as no type was specified.')

    unpacker_class = BaseUnpacker.index.get(tuple(_type))

    if unpacker_class:
        return unpacker_class

    raise NoSuchUnpackerError(_type=_type)
