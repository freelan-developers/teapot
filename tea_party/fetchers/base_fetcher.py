"""
A base Fetcher class.
"""


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

    def __init__(self, location, fetcher_class):
        """
        Create an UnsupportedLocationError for the specified `location` and
        `fetcher_class`.
        """

        super(UnsupportedLocationError, self).__init__(
            'The fetcher class %s does not support the specified location (%s)' % (
                fetcher_class,
                location,
            )
        )


class BaseFetcher(object):

    """
    Base class for all fetcher classes.

    If you subclass this class, you will have to re-implement the fetch()
    and normalize_location() methods in your subclass to provide your fetcher
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

    def __init__(self, location):
        """
        Instantiate a base fetcher.

        `location` is stored in self.location for use in derived classes.
        """

        self.location = self.normalize_location(location)

        if self.location is None:
            raise UnsupportedLocationError(
                location=location,
                fetcher_class=self.__class__,
            )

    def __repr__(self):
        """
        Get the representation of the fetcher.
        """

        return '<%s.%s(location=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.location,
        )

    def normalize_location(self, location):
        """
        Reimplement this method to indicate whether or not your fetcher class
        supports the specified `location` and to normalize its value.

        If the location is supported, this function must return a normalized
        location whose type depends on the fetcher implementation.

        If the location is not supported, this function must return None.
        """

        raise NotImplementedError

    def fetch(self, location, target):
        """
        Reimplement this method with your specific fetcher logic.

        This method must raise an exception on error.
        """

        raise NotImplementedError
