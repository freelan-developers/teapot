"""
A set of fetcher callbacks class.
"""

from progressbar import *


class BaseFetcherCallback(object):

    """
    Derive from this class to create a fetcher callback class.
    """

    def __init__(self, fetcher):
        """
        Create a new fetcher callback instance.

        `fetcher` is the fetcher instance to be associated with.
        """

        self.fetcher = fetcher

    def on_start(self, target, size):
        """
        The fetch just started.

        `target` is a user friendly name for the target being fetched.

        You may use a None `size` to indicate that the overall size is unknown.
        """

        pass

    def on_update(self, progress):
        """
        The fetch was updated.
        """

        pass

    def on_finish(self):
        """
        The fetch finished.
        """

        pass

    def on_exception(self, exception):
        """
        The fetch failed.

        Don't forget to call the on_finish() method if you override this
        method.
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

        self.progressbar.update(progress)

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
