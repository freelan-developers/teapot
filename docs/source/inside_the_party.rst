Inside the party
****************

This chapter describes how to write custom module-extensions for *teapot*.

Filters
=======

We already seen in :ref:`filters` what a :term:`filter` is. Now is the time to write your owns !

A :term:`filter` is a simple function that takes no parameters and returns a boolean value.

To register a new :term:`filter`, use the :func:`teapot.filters.decorators.named_filter` decorator.

.. autoclass:: teapot.filters.decorators.named_filter
    :members: __init__

Here is an example of some built-in :term:`filters<filter>`:

.. code-block:: python

    import os
    import sys

    from teapot.filters.decorators import named_filter

    @named_filter('windows')
    def windows():
        """
        Check if the platform is windows.
        """

        return sys.platform.startswith('win32')

    @named_filter('msvc', depends='windows')
    def msvc():
        """
        Check if MSVC is available.
        """

        return 'VCINSTALLDIR' in os.environ

Extensions
==========

As seen in :ref:`extensions`, an :term:`extension` is a function, that always takes a `builder` argument, optionally takes string parameters and returns a string.

:term:`Extensions<extension>` are to **teapot** what macros are to the C language.

To register a new :term:`extension`, use the :func:`teapot.extensions.decorators.named_extension` decorator.

.. autoclass:: teapot.extensions.decorators.named_extension
    :members: __init__

Here is an example of some built-in :term:`extensions<extension>`:

.. code-block:: python

    import os
    import sys

    from teapot.path import windows_to_unix_path
    from teapot.extensions.decorators import named_extension

    @named_extension('prefix')
    def prefix(builder, style='default'):
        """
        Get the builder prefix.
        """

        result = os.path.join(builder.attendee.party.prefix, builder.attendee.prefix, builder.prefix)

        if sys.platform.startswith('win32') and style == 'unix':
            result = windows_to_unix_path(result)

        return result

Note that the function **must** always have first `builder` argument that will be valued with the current :class:`teapot.builders.Builder` instance.

Fetchers
========

:term:`Fetchers<fetcher>` are responsible for downloading or copying the source archives from a specified location.

To define a new fetcher, just derive from :class:`teapot.fetchers.base_fetcher.BaseFetcher`.

.. autoclass:: teapot.fetchers.base_fetcher.BaseFetcher
    :members: read_source, do_fetch

Here is an example with the built-in *file* fetcher:

.. code-block:: python

    import os
    import shutil
    import mimetypes

    from teapot.fetchers.base_fetcher import BaseFetcher


    class FileFetcher(BaseFetcher):

        """
        Fetchs a file on the local filesystem.
        """

        shortname = 'file'

        def read_source(self, source):
            """
            Checks that the `source` is a local filename.
            """

            if os.path.isfile(source.location):
                self.file_path = os.path.abspath(source.location)

                return True

        def do_fetch(self, target):
            """
            Fetch a filename.
            """

            archive_path = os.path.join(target, os.path.basename(self.file_path))

            archive_type = mimetypes.guess_type(self.file_path)
            size = os.path.getsize(self.file_path)

            self.progress.on_start(target=os.path.basename(archive_path), size=size)

            shutil.copyfile(self.file_path, archive_path)

            # No real interactive progress to show here.
            #
            # This could be fixed though.

            self.progress.on_update(progress=size)
            self.progress.on_finish()

            return {
                'archive_path': archive_path,
                'archive_type': archive_type,
            }

Callbacks
---------

All callback classes derive from :class:`teapot.fetchers.callbacks.BaseFetcherCallback`.

.. autoclass:: teapot.fetchers.callbacks.BaseFetcherCallback
    :members: on_start, on_update, on_finish, on_exception

Unpackers
=========

:term:`Unpackers<unpacker>` are responsible for extracting the content of the source archives into an exploitable source tree.

To define a new unpacker, just derive from :class:`teapot.unpackers.base_unpacker.BaseUnpacker`.

.. autoclass:: teapot.unpackers.base_unpacker.BaseUnpacker
    :members: do_unpack

Here is an example with the built-in *tarball* unpacker:

.. code-block:: python

    from teapot.unpackers.base_unpacker import BaseUnpacker

    import os
    import tarfile


    class TarballUnpacker(BaseUnpacker):

        """
        An unpacker class that deals with .tgz files.
        """

        types = [
            ('application/x-gzip', None),
            ('application/x-bzip2', None),
        ]

        def do_unpack(self):
            """
            Uncompress the archive.

            Return the path of the extracted folder.
            """

            if not tarfile.is_tarfile(self.archive_path):
                raise InvalidTarballError(archive_path=self.archive_path)

            tar = tarfile.open(self.archive_path, 'r')

            # We get the common prefix for all archive members.
            prefix = os.path.commonprefix(tar.getnames())

            # An archive member with the prefix as a name should exist in the archive.
            while True:
                try:
                    prefix_member = tar.getmember(prefix)

                    if prefix_member.isdir:
                        break

                except KeyError:
                    pass

                new_prefix = os.path.dirname(prefix)

                if prefix == new_prefix:
                    raise TarballHasNoCommonPrefixError(archive_path=self.archive_path)
                else:
                    prefix = new_prefix

            source_tree_path = os.path.join(self.attendee.build_path, prefix_member.name)

            self.progress.on_start(count=len(tar.getmembers()))

            for index, member in enumerate(tar.getmembers()):
                if os.path.isabs(member.name):
                    raise ValueError('Refusing to extract archive that contains absolute filenames.')

                self.progress.on_update(current_file=member.name, progress=index)
                tar.extract(member, path=self.attendee.build_path)

            self.progress.on_finish()

            return {
                'source_tree_path': source_tree_path,
            }

Callbacks
---------

All callback classes derive from :class:`teapot.unpackers.callbacks.BaseUnpackerCallback`.

.. autoclass:: teapot.unpackers.callbacks.BaseUnpackerCallback
    :members: on_start, on_update, on_finish, on_exception

Party post-actions
==================

*post-actions* are simple function that takes a :class:`teapot.party.Party` instance as a parameter, and that gets executed right after a such instance was initialized.

You can register a *post-action* using the :func:`teapot.party.Party.register_post_action` decorator.

.. automethod:: teapot.party.Party.register_post_action

Here is an example a built-in *post-action* that registers the defaut environment:

.. code-block:: python

    @Party.register_post_action
    def add_default_environment(party):
        """
        Add the default environment to the party.
        """

        party.environment_register.register_environment(DEFAULT_ENVIRONMENT_NAME, create_default_environment())
