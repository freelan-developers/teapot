"""
A base Unpacker class.
"""

# TODO: Implement this
#from teapot.unpacker.callbacks import NullUnpackerCallback


class DuplicateUnpackerMimetypeError(ValueError):

    """
    An already existing mimetype was specified for a new BaseUnpacker subclass.
    """

    def __init__(self, mimetype, encoding, original_class, new_class):
        """
        Create a DuplicateUnpackerMimetypeError for the specified `mimetype`,
        `encoding`, `original_class` and `new_class`.
        """

        super(DuplicateUnpackerMimetypeError, self).__init__(
            'Cannot assign mimetype/encoding %r to %s as is already registered to %s' % (
                (mimetype, encoding),
                original_class,
                new_class,
            )
        )


class BaseUnpacker(object):

    """
    Base class for all unpacker classes.

    If you subclass this class, you will have to re-implement the
    :func:`do_unpack` method to provide your specific unpacker logic.

    If you desire to attach your unpacker to certain mimetypes, please do so by
    defining the class-level member `types` that must be a list of couples
    `(mimetype, encoding)`.
    """

    index = {}

    class __metaclass__(type):

        """
        A metaclass that automatically registers all BaseUnpacker subclasses
        that provide mimetype and encoding attributes in their definition.
        """

        def __init__(cls, name, bases, attrs):
            """
            Registers the class into the index if it has a shortname attribute
            in its definition.
            """

            type.__init__(cls, name, bases, attrs)

            if 'types' in attrs and cls.types:
                if not isinstance(cls.types, list):
                    raise TypeError(
                        'The types attribute for %s must be a list of 2-tuples.' %
                        cls)

                for mimetype, encoding in cls.types:
                    if (mimetype, encoding) in BaseUnpacker.index:
                        raise DuplicateUnpackerMimetypeError(
                            mimetype=mimetype,
                            encoding=encoding,
                            original_class=BaseUnpacker.index[(mimetype, encoding)],
                            new_class=cls,
                        )
                    else:
                        BaseUnpacker.index[(mimetype, encoding)] = cls
            else:
                # We ensure all unpacker classes have at least an empty
                # types attribute.
                setattr(cls, 'types', None)

    def __init__(self, attendee):
        """
        Create a new unpacker.
        """

        if not attendee:
            raise ValueError('An unpacker must be associated to an attendee.')

        self.attendee = attendee
        self.progress = self.attendee.party.unpacker_callback_class(self)

    def __repr__(self):
        """
        Get the representation of the unpacker.
        """

        return '<%s.%s()>' % (
            self.__class__.__module__,
            self.__class__.__name__,
        )

    @property
    def archive_path(self):
        """
        Get the archive path.

        This is a shortcut function for `self.attendee.archive_path`.
        """

        return self.attendee.archive_path

    def unpack(self):
        """
        Unpack the associated attendee archive.
        """

        try:
            return self.do_unpack()

        except Exception as ex:
            self.progress.on_exception(ex)

            raise

    def do_unpack(self):
        """
        Unpack an archive.

        The archive to unpack can be reached at `self.archive_path`.

        This method must return a dict with the following keys:
            - `source_tree_path`: The extracted source tree path.

        It must raise an exception on error.

        You can provide feedback on the unpacking operation by calling
        `self.progress.on_start`, `self.progress.on_update` and
        `self.progress.on_finish` at the appropriate time.

        See :class:`teapot.unpackers.callbacks.BaseUnpackerCallback` for
        further details.
        """

        raise NotImplementedError
