"""
A base Fetcher class.
"""

from tea_party.fetchers.callbacks import NullFetcherCallback


class DuplicateFetcherShortNameError(ValueError):

    """
    An already existing shortname was specified for a new BaseFetcher subclass.
    """

    def __init__(self, shortname, original_class, new_class):
        """
        Create a DuplicateFetcherShortNameError for the specified `shortname`,
        `original_class` and `new_class`.
        """

        super(DuplicateFetcherShortNameError, self).__init__(
            'Cannot assign shortname %r to %s as is already registered to %s' % (
                shortname,
                original_class,
                new_class,
            )
        )


class UnsupportedLocationError(ValueError):

    """
    A fetcher does not handle the specified location.
    """

    def __init__(self, source, fetcher_class):
        """
        Create an UnsupportedLocationError for the specified `source` and
        `fetcher_class`.
        """

        super(UnsupportedLocationError, self).__init__(
            'The fetcher class %s does not support the specified source (%s)' % (
                fetcher_class,
                source,
            )
        )


class BaseFetcher(object):

    """
    Base class for all fetcher classes.

    If you subclass this class, you will have to re-implement the do_fetch()
    and read_source() methods in your subclass to provide your fetcher
    specific fetch logic.
    """

    index = {}

    class __metaclass__(type):

        """
        A metaclass that automatically registers all BaseFetcher subclasses
        that provide a shortname attribute in their definition.
        """

        def __init__(cls, name, bases, attrs):
            """
            Registers the class into the index if it has a shortname attribute
            in its definition.
            """

            type.__init__(cls, name, bases, attrs)

            if 'shortname' in attrs and cls.shortname:
                if not isinstance(cls.shortname, basestring):
                    raise TypeError(
                        'The shortname attribute for %s must be a string.' %
                        cls)

                if cls.shortname in BaseFetcher.index:
                    raise DuplicateFetcherShortNameError(
                        shortname=cls.shortname,
                        original_class=BaseFetcher.index[cls.shortname],
                        new_class=cls,
                    )
                else:
                    BaseFetcher.index[cls.shortname] = cls
            else:
                # We ensure all fetcher classes have at least an empty
                # shortname attribute.
                setattr(cls, 'shortname', None)

    def __init__(self, source):
        """
        Instantiate a base fetcher.

        `source` is the source.
        """

        if not source:
            raise ValueError('A fetcher must be associated to a source.')

        if not self.read_source(source):
            raise UnsupportedLocationError(
                source=source,
                fetcher_class=self.__class__,
            )

        self.source = source
        self.progress = source.attendee.party.fetcher_callback_class(self)

    def __repr__(self):
        """
        Get the representation of the fetcher.
        """

        return '<%s.%s(source=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.source,
        )

    def read_source(self, source):
        """
        Reimplement this method to indicate whether or not your fetcher class
        supports the specified `source`.

        This method is called during the fetcher creation and must return a
        truthy value if the fetcher supports the specified source.

        You may set custom instance variable in this method as it is guaranteed
        that it gets called before the fetch() method. For instance, one could
        parse a source URL and get the meaningful components into member
        variables for later use in do_fetch().
        """

        raise NotImplementedError

    def fetch(self, target):
        """
        Fetch the associated source using `target` as a suggested filename.
        """

        try:
            return self.do_fetch(target)

        except Exception as ex:
            self.progress.on_exception(ex)

            raise

    def do_fetch(self, target):
        """
        Reimplement this method with your specific fetcher logic.

        `target` is the suggested target filename.

        This method must return a dict with the following keys:
            - archive_path: The archive absolute path.
            - archive_type: A couple containing the mimetype, then the encoding
            of the archive. Example: ('application/x-gzip', None)

        It must raise an exception on error.

        You can provide feedback on the fetching operation by calling
        `self.progress.on_start`, `self.progress.on_update` and
        `self.progress.on_finish` at the appropriate time.
        """

        raise NotImplementedError
