"""
A base environment class.
"""

class BaseEnvironment(object):

    """
    Base class for all environment classes.

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
