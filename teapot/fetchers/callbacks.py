"""
A set of fetcher callbacks class.
"""

from progressbar import *


class BaseFetcherCallback(object):

    """
    Derive from this class to create a fetcher callback class.
    """

    def on_start(self, target, size):
        """
        Call this method when the fetch is about to begin.

        `target` is the user-friendly name for the target being fetched.
        `size` is the size, in bytes, of the archive that is being fetched.

        You may use a None `size` to indicate that the overall size is unknown.
        """

        pass

    def on_update(self, progress):
        """
        Call this method whenever the fetch had some progress.

        `progress` is the number of bytes that were already fetched.
        """

        pass

    def on_finish(self):
        """
        Call this method when the fetch is over.
        """

        pass

    def on_exception(self, exception):
        """
        Call this method when a fatal exception is raised that must abort the
        fetch.

        The base implementation calls the :func:`on_finish` method and if you
        override this method, you must do the same (or just call the base
        method).
        """

        self.on_finish()


class NullFetcherCallback(BaseFetcherCallback):
    """
    Provides no callback.
    """

    pass


class ProgressBarFetcherCallback(BaseFetcherCallback):
    """
    Provides a progress bar callback to fetchers.
    """

    def on_start(self, target, size):
        """
        The fetch just started.

        You use a None `size` to indicate that the overall size is unknown.
        """

        widgets = [target, ': ', Bar(marker='#', left='[', right='] '), Percentage(), ' - ', FileTransferSpeed()]

        if size:
            widgets.extend([' - ', 'Total size: %s MB' % round(size / (1024 ** 2), 2)])

        self.progressbar = ProgressBar(widgets=widgets, maxval=size)
        self.progressbar.start()

    def on_update(self, progress):
        """
        The fetch was updated.
        """

        try:
            self.progressbar.update(progress)
        except ValueError:
            pass

    def on_finish(self):
        """
        The fetch finished.
        """

        self.progressbar.finish()

    def on_exception(self, exception):
        """
        The fetch failed.
        """

        if hasattr(self, 'progressbar'):
            self.on_finish()
