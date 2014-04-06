"""
A base Fetcher class.
"""

from ..memoized import MemoizedObject
from ..log import Highlight as hl

from .callbacks import ProgressBarFetcherCallback


class FetcherImplementation(object):
    """
    Base class for all fetcher implementation classes.
    """

    def parse_source(self, source):
        """
        Reimplement this method to indicate whether or not your fetcher class
        supports the specified `source`.

        Upon success, this method should return a truthy value if the specified
        `source` is supported by the fetcher. This truthy value will be passed
        as the `parsed_source` attribute to fetch().
        """

        raise NotImplementedError

    def fetch(self, parsed_source, target_path, progress):
        """
        Reimplement this method with your specific fetcher logic.

        `source` is the source to fetch.
        `target_path` is the path to the target.
        `progress` is an instance of a fetcher callback used to report progress
        to the user.

        This method must return a tuple with the following values:
            - `archive_path`: The archive absolute path.
            - `archive_type`: A couple containing the mimetype, then the
              encoding of the archive. Example: ``('application/x-gzip', None)``

        It must raise an exception on error.

        You can (and should) provide feedback on the fetching operation by
        calling `self.progress.on_start`, `self.progress.on_update` and
        `self.progress.on_finish` at the appropriate time.

        See :class:`teapot.fetchers.callbacks.BaseFetcherCallback`
        documentation for details.
        """

        raise NotImplementedError


class Fetcher(MemoizedObject):

    """
    Represent a fetcher.

    If you subclass this class, you will have to re-implement the
    :func:`read_source` and :func:`do_fetch` methods in your subclass to
    provide your fetcher specific fetch logic.

    If you intend to expose your fetcher to users, you must also declare a
    unique class-level `shortname`. This is what the user will specify in the
    :term:`party file` to use a specific fetcher.
    """

    @classmethod
    def get_instance_or_fail(cls, name):
        fetcher = cls.get_instance(name)

        if fetcher is None:
            raise TeapotError("Unable to find the fetcher named %s.", hl(name))

        return fetcher

    @classmethod
    def get_instance_for(cls, source, default=None):
        for instance in cls.get_instances():
            if instance.can_parse_source(source):
                return instance

        return default

    def __init__(self, fetcher_impl_class, progress_class=ProgressBarFetcherCallback):
        """
        Create a new fetcher that uses the specified fetcher
        implementation.
        """

        self._fetcher_impl = fetcher_impl_class()
        self.progress = progress_class()

    def can_parse_source(self, source):
        """
        Check if a fetcher can parse the specified source.
        """

        return self._fetcher_impl.parse_source(source=source)

    def fetch(self, source, target_path):
        """
        Fetch the specified `source` using `target_path` as the target path.

        If fetching is not supported, a falsy value is returned.
        """

        try:
            parsed_source = self._fetcher_impl.parse_source(source=source)

            if not parsed_source:
                return False

            return self._fetcher_impl.fetch(
                parsed_source=parsed_source,
                target_path=target_path,
                progress=self.progress
            )

        except Exception as ex:
            self.progress.on_exception(ex)

            raise


class register_fetcher(object):
    """
    A decorator that registers a fetcher.
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        with Fetcher.raise_on_duplicate():
            Fetcher(name=self.name, fetcher_impl_class=cls)

        return cls
