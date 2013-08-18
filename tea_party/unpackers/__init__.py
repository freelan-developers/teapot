"""
Contains all tea-party unpackers logic.

If you want to create your own unpacker, derive from
tea_party.unpackers.base_unpacker.BaseUnpacker.
"""

from tea_party.fetchers.base_unpacker import BaseUnpacker, UnsupportedMimetypeError


class NoSuchUnpackerError(ValueError):

    """
    Raised when a non-existing unpacker was requested.
    """

    def __init__(self, mimetype):
        """
        Create a NoSuchUnpackerError instance for the specified `mimetype`.
        """

        super(
            NoSuchUnpackerError,
            self
        ).__init__(
            'No unpacker for the mimetype: %r' % mimetype
        )


def get_unpacker_class_from_mimetype(mimetype):
    """
    Get the appropriate unpacker class/builder from its `mimetype`.

    If no unpacker supports `mimetype` a NoSuchFetcherError instance is raised.
    """

    unpacker_class = BaseUnpacker.index.get(mimetype)

    if unpacker_class:
        return unpacker_class

    raise NoSuchUnpackerError(mimetype=mimetype)
