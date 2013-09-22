The party file
**************

The *party file* is at the heart of **tea-party**. It describes the different third-party softwares to build, and how to build them.

Terminology
===========

Before going any further, here are something that could come handy:

party file
  The party file is a YAML file, named `party.yaml` that can be located anywhere. Within this file, almost all paths are relative to the party file directory.
attendee
  An attendee is a fancy name for a third-party software to build. A *party file* can contain as many attendees as you like, and different attendees can even represent the same third-party software if that makes sense in your situation.
source
  A source designates the location and the method where and how to fetch the source files for an attendee. While the most common case is downloading a file using HTTP, one can also copy a file locally, through a network share or from Github.
fetcher
  A fetcher is the entity that is responsible for handling a specific type of source. Usually, fetchers are smart enough to recognize sources from their format and you should not have to care too much about them.
unpacker
  An unpacker is the entity that is responsible for turning a compressed archive (ZIP file or `.tar.gz` for instance) into a source tree.
builder
  A builder is the list of commands to execute in order to transform the attendee source into a compiled set of binaries (or whatever a build process can produce). Builders rely a lot on *environments*.
environment
  An environment is a set of environment variables, shell value and inheritance parameters that wraps one or several builds. An environment defines the tools to use and their options.

Structure
=========

The party file is a YAML file whose root element is a dictionary. While YAML files can make use of a lot of complex data structures, **tea-party** only makes use of the common ones, namely:

 - dictionaries
 - lists
 - strings
 - booleans
 - null

.. note:: The fact that **tea-party** doesn't make use of other data structures doesn't mean you can't use those; you can actually do and use whatever you want when writing custom extensions.

The definition order of all elements in dictionaries is unspecified. This means **tea-party** will not care at all in which order you write the keys of a dictionary.

Strings can be any unicode string, however it is **strongly** recommended that you stick with ANSI characters, especially when it comes to indexes.

Attendees
---------

The attendees are a first-level element of the root dictionary. They are declared within a dictionary named `attendees` whose each key is the index of an attendee, and whose values are the attendees themselves.

Here is an example that declares two attendees:

.. code-block:: yaml

    attendees:
      libiconv:
        source: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz
      libcurl:
        source: http://curl.haxx.se/download/curl-7.32.0.tar.gz

This example, while perfectly valid, is not quite complete: as they are written, those attendees would be able to download and unpack the specified archives, but they don't know how to build the software they constitute.

Here is a more complete party file with an attendee that actually does something:

.. code-block:: yaml

    attendees:
      libiconv:
        source: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz
        builders:
          default:
            commands:
              - ./configure --prefix={{prefix}}
              - make
              - make install

This party file defines completely the way to build *libicon, version 1.14*. The archive will be downloaded from the specified URL, it will be extracted and build with the usuall autotools scenario (`./configure && make && make install`).

In the ``./configure`` command, you may notice the specific ``--prefix={{prefix}}`` syntax. This makes uses of an *extension* that will be replaced on runtime by the *prefix* path for this build.

You may find more information on builders in the :ref:`builders` section.

Sources
+++++++

The `source` directive in an *attendee* can take several forms.

The simpler form is a *location string*. The possible formats for this depends on the registered *fetchers*.

Here are the default fetchers and their supported formats:

`http`
  Fetches an archive from a web URL in a fashion similar to the :command:`wget` command. This is the most commonly used fetcher.

  Example formats:
   - ``http://host/path/archive.zip``
   - ``https://host/path/archive.zip``

`file`
  Fetches an archive from a filesystem path. The path can be either local or a network mount point.

  Example formats:
   - ``~/archives/archive.tar.gz``
   - ``C:\archives\archive.zip``

`github`
  Generates and fetches an archive from a Github-hosted project.

  Example formats:
   - ``github:user/repository/ref``

`source` can also be a dict of attributes, like so:

.. code-block:: yaml

    attendees:
      libiconv:
        source:
          location: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz
          type: application/x-gzip
          fetcher: http
          fetcher_options:
          filters: unix

All these attributes, except `location` are optional.

`location`
  A *location string* as they were just described.

`type`
  The mimetype of the archive. Can also be a list of two elements `[mimetype, encoding]` for more complex mimetypes.

`fetcher`
  The fetcher to use. Specifying a fetcher disables the automatic fetcher type selection. Specifying a fetcher only makes sense if the location string is ambiguous, which cannot happen with the built-in fetchers.

`fetcher_options`
  A dictionary of options for the fetcher. Built-in fetchers do not take any option.

`filters`
  A list of filters that the current execution environment must match in order for the source to be active. For instance, one can use filters to specify different sources for Windows and Linux, within the same attendee.

For more complex situations, `source` can also be a list of either *location strings* or attributes dictionary (optionaly mixed), like so:

.. code-block:: yaml

    attendees:
      libiconv:
        source:
          -
            location: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14_some-variant.tar.gz
            type: application/x-gzip
            fetcher: http
            fetcher_options:
            filters: windows
          - http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz

Sources are tried in the declaration order for a given attendee. In this example, when `teapot` tries to download the archive for the attendee, it will first try the first one, only on Windows. If the first one fails (say because of a network error), or if `teapot` is run on a Unix variant, it will skip to the second source.

You may also extend tea-party and implement your own fetchers, should you have specific needs.

Unpackers
+++++++++

At some point before the build, `teapot` must convert a downloaded (often compressed) archive into a source tree. This is what *unpackers* are for.

The unpacker selection is done automatically, depending on the mimetype of the downloaded archive. That is, the only way to choose which unpacker to use, is to change the mimetype of the attendee.

By default, *tea-party* provides the following unpackers:

Tarball unpacker
  An unpacker that can uncompress tarballs (`.tar.gz` and `.tar.bz2` files).

  It recognizes the following mimetypes:
   - :mimetype:`application/x-gzip`
   - :mimetype:`application/x-bzip2`

Zipfile unpacker
  An unpacker that can uncompress zip archives (`.zip` files).

  It recognizes only the :mimetype:`application/zip` mimetype.

You may also extend tea-party and implement your own unpackers, should you have specific needs.

.. _builders:

Builders
++++++++

One of the most important thing to declare into an attendee, is its builders. A builder is responsible for taking an unarchived source tree and creating something by issuing a series of commands.

Builders are declared like so:

.. code-block:: yaml

    attendees:
      libiconv:
        source: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz
        builders:
          mybuild:
            commands:
              - ./configure --prefix={{prefix}}
              - make
              - make install

In this simple example, `teapot` will go into the source tree unpacked from `libiconv-1.14.tar.gz` and will issue the following commands, in order:
 - ``./configure --prefix={{prefix}}``
 - ``make``
 - ``make install``

If all of these commands succeed, the build is considered successful as well.

.. note:: Here ``{{prefix}}`` is an extension that resolves at runtime as the current prefix for the builder. You can learn more about extensions in the :ref:`extensions` section.

One attendee can have as many different builders as you want it to have. All the builders are entries of the `builders` dictionary where the key is the builder name, and the value if a dictionary of attributes for the builder.

A builder supports the following attributes:

`commands`
  Can be either a string with a single command to execute or a list of commands to execute.

  Commands can contain :ref:`extensions<extensions>` and environment variables that will be substituted upon execution.

`environment`
  The environment in which the build must take place.

  If no environment is specified, the *default* environment is taken, which is the one the `teapot` command is running in.

  You can learn more about environments in the :ref:`environments` section.

`tags`
  A list of tags for the builder.

  Tags can be used later on by the `teapot` command to restrict the builders to run dynamically.

  One common use for tags is to differentiate builders for different build architectures (`x86` and `x64` for instance).

`filters`
  A list of filters that the current execution environment must match in order for the builder to be active. For instance, one can use filters to specify different sources for Windows and Linux, within the same attendee.

`prefix`
  The builder specific prefix.

  The content of this value is used by the `prefix` extension at runtime.

  If `prefix` is a relative path, it will be appended to the attendee's prefix.

  If `prefix` is an absolute path, it will be taken as it is. 

  If `prefix` is `True`, it will take the name of the builder as a value. Use this to differentiate builds outputs easily for a given attendee.

.. _environments:

Environments
------------

.. _filters:

Filters
-------

.. _extensions:

Extensions
----------

Other settings
--------------

Using `teapot`
==============

.. toctree::
   :maxdepth: 2
