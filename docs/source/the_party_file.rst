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
  A fetcher is the entity that is responsible for handling a specific type of source. Usually, fetchers are smart enough to recognize sources from their format and you should have to care too much about them.
unpacker
  An unpacker is the entity that is responsible for turning a compressed archive (ZIP file or `.tar.gz` for instance) into a source files directory.
build
  A build is the list of commands to execute in order to transform the attendee source into a compiled set of binaries (or whatever a build process can produce). Builds rely a lot on *environments*.
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


.. toctree::
   :maxdepth: 2
