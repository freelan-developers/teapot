"""
A set of unpacker callbacks class.
"""

import os

from progressbar import *


class BaseUnpackerCallback(object):

    """
    Derive from this class to create an unpacker callback class.
    """

    def on_start(self, archive_path, count):
        """
        Call this method when the unpacking is about to start.

        `archive_path` is the path of the extracted archive.
        `count` indicates the total count of files in the archive.

        You may use a None `count` to indicate that the overall count is
        unknown.
        """

        pass

    def on_update(self, current_file, progress):
        """
        Call this method when the unpacking had some progress.

        `current_file` indicates the file currently being unpacked.
        `progress` indicates the number of the current file in the archive.
        """

        pass

    def on_finish(self):
        """
        Call this method when the unpacking is complete.
        """

        pass

    def on_exception(self, exception):
        """
        Call this method when a fatal exception is raised that must abort the
        unpack.

        The base implementation calls the :func:`on_finish` method and if you
        override this method, you must do the same (or just call the base
        method).
        """

        self.on_finish()


class NullUnpackerCallback(BaseUnpackerCallback):
    """
    Provides no callback.
    """

    pass


class CurrentFile(WidgetHFill):
    """Displays the current file."""

    def __init__(self, unpacker_callback, prefix='', suffix=''):
        """
        Create a current file widget.
        """

        self.unpacker_callback = unpacker_callback
        self.count = 0
        self.prefix = prefix
        self.suffix = suffix

    def update(self, pbar, width):
        """
        Update the progress bar.
        """

        if self.unpacker_callback.current_file:
            result = self.prefix + self.unpacker_callback.current_file + self.suffix
        else:
            result = ''

        if len(result) > width:
            result = result[:width - 3 - len(self.suffix)] + '...' + self.suffix
        else:
            result += ' ' * (width - len(result))

        return result


class ProgressBarUnpackerCallback(BaseUnpackerCallback):
    """
    Provides a progress bar callback to unpackers.
    """

    def on_start(self, archive_path, count):
        """
        The unpack just started.
        """

        self.count = count
        self.current_file = ''

        widgets = [os.path.basename(archive_path), ': ', SimpleProgress(), ' (', Percentage(), ')', CurrentFile(self, prefix=' - ')]
        self.progressbar = ProgressBar(widgets=widgets, maxval=count)
        self.progressbar.start()

    def on_update(self, current_file, progress):
        """
        The unpack was updated.
        """

        self.current_file = current_file
        self.progressbar.update(progress)

    def on_finish(self):
        """
        The unpack finished.
        """

        self.current_file = ''
        self.progressbar.update(self.count)
        self.progressbar.finish()

    def on_exception(self, exception):
        """
        The unpack failed.
        """

        if hasattr(self, 'progressbar'):
            self.on_finish()
