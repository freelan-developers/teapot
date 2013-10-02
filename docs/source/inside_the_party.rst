Inside the party
****************

This chapter describes how to write custom module-extensions for *tea-party*.

Filters
=======

We already seen in :ref:`filters` what a :term:`filter` is. Now is the time to write your owns !

A :term:`filter` is a simple function that takes no parameters and returns a boolean value.

To register a new :term:`filter`, use the :func:`tea_party.filters.decorators.named_filter` decorator.

.. autoclass:: tea_party.filters.decorators.named_filter
    :members: __init__

Here is an example of some built-in :term:`filters<filter>`:

.. code-block:: python

    import os
    import sys

    from tea_party.filters.decorators import named_filter

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

:term:`Extensions<extension>` are to **tea-party** what macros are to the C language.

To register a new :term:`extension`, use the :func:`tea_party.extensions.decorators.named_extension` decorator.

.. autoclass:: tea_party.extensions.decorators.named_extension
    :members: __init__

Here is an example of some built-in :term:`extensions<extension>`:

.. code-block:: python

    import os
    import sys

    from tea_party.path import windows_to_unix_path
    from tea_party.extensions.decorators import named_extension

    @named_extension('prefix')
    def prefix(builder, style='default'):
        """
        Get the builder prefix.
        """

        result = os.path.join(builder.attendee.party.prefix, builder.attendee.prefix, builder.prefix)

        if sys.platform.startswith('win32') and style == 'unix':
            result = windows_to_unix_path(result)

        return result

Note that the function **must** always have first `builder` argument that will be valued with the current :class:`tea_party.builders.Builder` instance.

Fetchers
========

:term:`Fetchers<fetcher>` are responsible for downloading or copying the source archives from a specified location.

To define a new fetcher, just derive from :class:`tea_party.fetchers.base_fetcher.BaseFetcher`.

.. autoclass:: tea_party.fetchers.base_fetcher.BaseFetcher
    :members: read_source, do_fetch

Here is an example with the built-in *file* fetcher:

.. code-block:: python

    import os
    import shutil
    import mimetypes

    from tea_party.fetchers.base_fetcher import BaseFetcher


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

All callback classes derive from :class:`tea_party.fetchers.callbacks.BaseFetcherCallback`.

.. autoclass:: tea_party.fetchers.callbacks.BaseFetcherCallback
    :members: on_start, on_update, on_finish, on_exception

Unpackers
=========

Party post-actions
==================
