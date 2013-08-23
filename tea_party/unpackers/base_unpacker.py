"""
A base Unpacker class.
"""

# TODO: Implement this
#from tea_party.unpacker.callbacks import NullUnpackerCallback


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


class UnsupportedArchiveError(RuntimeError):

    """
    The specified archive format is not supported by the current unpacker.
    """

    def __init__(self, archive_path):
        """
        Create an UnsupportedArchiveError for the specified `archive_path`.
        """

        super(UnsupportedArchiveError, self).__init__(
            'Unsupported archive: %s' % archive_path
        )


class BaseUnpacker(object):

    """
    Base class for all unpacker classes.

    If you subclass this class, you will have to re-implement the unpack()
    method.
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

            if 'mimetypes_encodings' in attrs and cls.mimetypes_encodings:
                if not isinstance(cls.mimetypes_encodings, list):
                    raise TypeError(
                        'The mimetypes_encodings attribute for %s must be a list of 2-tuples.' %
                        cls)

                for mimetype, encoding in cls.mimetypes_encodings:
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
                # mimetypes_encodings attribute.
                setattr(cls, 'mimetypes_encodings', None)

    def __repr__(self):
        """
        Get the representation of the unpacker.
        """

        return '<%s.%s()>' % (
            self.__class__.__module__,
            self.__class__.__name__,
        )

    def unpack(self, archive_path):
        """
        Unpack an archive.

        Define this method in a subclass and return the path to the extracted
        folder that contains the source.

        If the unpacker doesn't support the specified archive, raise an
        exception.
        """

        raise NotImplementedError
