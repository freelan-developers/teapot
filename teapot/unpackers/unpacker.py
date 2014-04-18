"""
A base Unpacker class.
"""

from ..memoized import MemoizedObject
from ..log import Highlight as hl

from .callbacks import ProgressBarUnpackerCallback


class UnpackerImplementation(object):

    """
    Base class for all unpacker implementation classes.
    """

    def unpack(self, archive_path, target_path, progress):
        """
        Unpack the specified archive.

        `archive_path` is the path of the archive to unpack.
        `target_path` is the path to extract the archive to.

        It returns the unpack manifest.
        """

        raise NotImplementedError


class Unpacker(MemoizedObject):

    """
    Represent an unpacker.
    """

    memoization_keys = ('mimetype',)
    no_such_instance_message = "Unable to find an unpacker that handles archives of type %s."
    no_such_instance_args = ('self',)

    @staticmethod
    def mimetype_to_str(mimetype):
        return '(%s)' % ','.join(x for x in mimetype if x)

    def __init__(self, unpacker_impl_class, progress_class=ProgressBarUnpackerCallback):
        """
        Create a new unpacker that uses the specified unpacker
        implementation.
        """

        self._unpacker_impl = unpacker_impl_class()
        self.progress = progress_class()

    def __str__(self):
        return mimetype_to_str(self.mimetype)

    def unpack(self, archive_path, target_path):
        """
        Unpack the specified archive.

        `archive_path` is the path of the archive to unpack.
        `target_path` is the path to extract the archive to.

        It returns the unpack manifest.
        """

        try:
            return self._unpacker_impl.unpack(
                archive_path=archive_path,
                target_path=target_path,
                progress=self.progress,
            )

        except Exception as ex:
            self.progress.on_exception(ex)

            raise


class register_unpacker(object):
    """
    A decorator that registers an unpacker.
    """

    def __init__(self, mimetype):
        self.mimetype = mimetype

    def __call__(self, cls):
        with Unpacker.raise_on_duplicate():
            Unpacker(mimetype=self.mimetype, unpacker_impl_class=cls)

        return cls
