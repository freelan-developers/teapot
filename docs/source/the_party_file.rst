The :term:`party file`
**********************

The :term:`party file` is at the heart of **tea-party**. It describes the different third-party softwares to build, and how to build them.

Structure
=========

The :term:`party file` is a YAML file whose root element is a dictionary. While YAML files can make use of a lot of complex data structures, **tea-party** only makes use of the common ones, namely:

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

The :term:`attendees<attendee>` are a first-level element of the root dictionary. They are declared within a dictionary named :term:`attendees<attendee>` whose each key is the index of an :term:`attendee`, and whose values are the :term:`attendees<attendee>` themselves.

Here is an example that declares two :term:`attendees<attendee>`:

.. code-block:: yaml

    attendees:
      libiconv:
        source: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz
      libcurl:
        source: http://curl.haxx.se/download/curl-7.32.0.tar.gz

This example, while perfectly valid, is not quite complete: as they are written, those :term:`attendees<attendee>` would be able to download and unpack the specified archives, but they don't know how to build the software they constitute.

Here is a more complete :term:`party file` with an :term:`attendee` that actually does something:

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

This :term:`party file` defines completely the way to build *libicon, version 1.14*. The archive will be downloaded from the specified URL, it will be extracted and built with the usuall autotools scenario (`./configure && make && make install`).

In the ``./configure`` command, you may notice the specific ``--prefix={{prefix}}`` syntax. This makes uses of an *extension* that will be replaced on runtime by the *prefix* path for this build.

You may find more information on :term:`builders<builder>` in the :ref:`builders` section.

An attendee can have the following attributes:

`source`
  The source of the attendee. More on that in :ref:`sources`.

`filters`
  A list of :term:`filters<filter>` that the current execution environment must match in order for the attendee to be active. For instance, one can use filters to specify different attendees for Windows and Linux, within the same :term:`party file`.

`builders`
  A dictionary of :term:`builders<builder>` that specify what to do with the source code. More on that in :ref:`builders`.

`depends`
  A list of names of other :term:`attendees<attendee>` that this :term:`attendee` depends on for building.

  `depends` can also be a single string in case the :term:`attendee` only depends on one other :term:`attendee`.

`prefix`
  The :term:`attendee` specific prefix.

  The content of this value is used by the `prefix` extension at runtime.

  If `prefix` is a relative path, it will be appended to the :term:`party file`'s prefix.

  If `prefix` is an absolute path, it will be taken as it is. 

  If `prefix` is `True`, it will take the name of the :term:`attendee` as a value. Use this to differentiate builds outputs directories for different :term:`attendees<attendee>`.

.. warning::

    If the dependency graph is cyclic, :term:`teapot` will notice it before even starting the build and will warn you about the problem.

.. _sources:

Sources
+++++++

The `source` directive in an :term:`attendee` can take several forms.

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
  A list of filters that the current execution environment must match in order for the source to be active. For instance, one can use filters to specify different sources for Windows and Linux, within the same :term:`attendee`.

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

Sources are tried in the declaration order for a given :term:`attendee`. In this example, when :term:`teapot` tries to download the archive for the :term:`attendee`, it will first try the first one, only on Windows. If the first one fails (say because of a network error), or if :term:`teapot` is run on a Unix variant, it will skip to the second source.

You may also extend tea-party and implement your own fetchers, should you have specific needs.

Unpackers
+++++++++

At some point before the build, :term:`teapot` must convert a downloaded (often compressed) archive into a source tree. This is what *unpackers* are for.

The unpacker selection is done automatically, depending on the mimetype of the downloaded archive. That is, the only way to choose which unpacker to use, is to change the mimetype of the :term:`attendee`.

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

One of the most important thing to declare into an :term:`attendee`, is its :term:`builders<builder>`. A :term:`builder` is responsible for taking an unarchived source tree and creating something by issuing a series of commands.

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

In this simple example, :term:`teapot` will go into the source tree unpacked from `libiconv-1.14.tar.gz` and will issue the following commands, in order:
 - ``./configure --prefix={{prefix}}``
 - ``make``
 - ``make install``

If all of these commands succeed, the build is considered successful as well.

.. note:: Here ``{{prefix}}`` is an extension that resolves at runtime as the current prefix for the :term:`builder`. You can learn more about extensions in the :ref:`extensions` section.

One :term:`attendee` can have as many different :term:`builders<builder>` as you want it to have. All the :term:`builders<builder>` are entries of the `builders` dictionary where the key is the :term:`builder` name, and the value if a dictionary of attributes for the :term:`builder`.

Here is an example of a more complex :term:`attendee`:

.. code-block:: yaml

    attendees:
      libiconv:
        source: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz
        builders:
          default_x86:
            filters:
              - windows
              - mingw
            environment: mingw_x86
            tags: x86
            commands:
              - ./configure --prefix={{prefix(unix)}}
              - make
              - make install
            prefix: True

          default_x64:
            filters:
              - windows
              - mingw
            environment: mingw_x64
            tags: x64
            commands:
              - ./configure --prefix={{prefix(unix)}}
              - make
              - make install
            prefix: True

In this example, we define two builders (`default_x86` and `default_x64`) that have exactly the same build commands.

Both are to be executed if, and only if, MinGW is available in the execution environment. They each make use of a customized :term:`environment` (more on that in :ref:`environments`).

Also note that a tag has been added for every one of them, so that the user can easily choose between x86 and x64 builds when using :term:`teapot`.

Inside the :term:`party file`, the `builder` dictionary supports the following attributes:

`commands`
  Can be either a string with a single command to execute or a list of commands to execute.

  Commands can contain :ref:`extensions<extensions>` and environment variables that will be substituted upon execution.

`environment`
  The environment in which the build must take place.

  If no environment is specified, the *default* environment is taken, which is the one the :term:`teapot` command is running in.

  You can learn more about environments in the :ref:`environments` section.

`tags`
  A list of tags for the :term:`builder`.

  Tags can be used later on by the :term:`teapot` command to restrict the :term:`builders<builder>` to run dynamically.

  One common use for tags is to differentiate :term:`builders<builder>` for different build architectures (`x86` and `x64` for instance).

`filters`
  A list of filters that the current execution environment must match in order for the :term:`builder` to be active. For instance, one can use filters to specify different builders for Windows and Linux, within the same :term:`attendee`.

`prefix`
  The :term:`builder` specific prefix.

  The content of this value is used by the `prefix` extension at runtime.

  If `prefix` is a relative path, it will be appended to the :term:`attendee`'s prefix.

  If `prefix` is an absolute path, it will be taken as it is. 

  If `prefix` is `True`, it will take the name of the :term:`builder` as a value. Use this to differentiate builds outputs easily for a given :term:`attendee`.

.. _environments:

Environments
------------

Environments define the execution environment of a :term:`builder`.

They can be defined either at the attendee level (within a :term:`builder` declaration), or inside the global `environments` dictionary, at the root of :term:`party file`.

An :term:`environment` can inherit from another **named** :term:`environment`.

Here is an example of :term:`party file` that defines environments:

.. code-block:: yaml

    attendees:
      libiconv:
        source: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz
        builders:
          default_x86:
            environment: mingw_x86
            tags: x86
            commands:
              - ./configure --prefix={{prefix(unix)}}
              - make
              - make install
            prefix: True

          default_x64:
            environment: mingw_x64
            tags: x64
            commands:
              - ./configure --prefix={{prefix(unix)}}
              - make
              - make install
            prefix: True

    environments:
      mingw_x86:
        shell: ["C:\\MinGW\\msys\\1.0\\bin\\bash.exe", "-c"]
        inherit: default
        variables:
          PATH: "C:\\MinGW32\\bin:%PATH%"

      mingw_x64:
        shell: ["C:\\MinGW\\msys\\1.0\\bin\\bash.exe", "-c"]
        inherit: default
        variables:
          PATH: "C:\\MinGW64\\bin:%PATH%"

In this example, we define two environments that use the same :term:`shell` (here, `bash` for Windows). They both inherit from the `default` environment and each (re)define the :envvar:`PATH` environment variable.

An `environment` dictionary understands the following attributes:

`shell`
  The :term:`shell` to use.

  `shell` can be a list of command arguments (with the executable as the first argument). This is the recommended way of specifying the :term:`shell` as it is unambiguous.

  If `shell` is a string, it will be parsed and split into a list using :func:`shlex.split`. This method of defining the shell and its arguments can be ambiguous and is therefore **not recommended**.

  `shell` can also be :const:`True` (the default), in which case its value will be taken from the inherited :term:`environment`, if it has one.

  If no `shell` is specified, the default one from the system will be taken as specified in :func:`subprocess.call`.

`variables`
  A dictionary of environment variables to set, remove or override.

  Each variable can be set to either a string, or to ``null`` (the YAML equivalent of :const:`None`).

  The behavior a null value depends on the value of `inherit`.

  If the :term:`environment` inherits its attributes from another :term:`environment`, a null value indicates that the environment variable should be **removed** from the environment. This is **not** equivalent to setting its value to an empty string (in this case the variable would still be part of the environment, but would just be empty).

  If the :term:`environment` does not inherit its attributes from another :term:`environment`, a null value indicates that the value for this environment variable should be the one of the execution environment (the environment into which :term:`teapot` was called). If the environment variable was not set within the execution environment, it won't be set in the new environment if its value was ``null``.

`inherit`
  `inherit` can be null (the default), or it can be the name of a named :term:`environment` to inherit from.

  If `inherit` is null, none of the existing environment variables are inherited and only the ones defined in the `variables` attribute will be set.

.. note::

    By default, *tea-party* exposes the execution environment through the name ``default``.

    This ``default`` environment has all the environment variables that were set right before the call to :term:`teapot` and uses the default system :term:`shell`.

.. _filters:

Filters
-------

Filters are a way to differentiate :term:`teapot` execution accross platforms and environments. A :term:`filter` is basically a test whose result is boolean. It answers a simple question like: am on Windows ? Is MinGW available ?

*tea-party* comes with several built-in filters:

========= ====================================================================================
Filter    Role
========= ====================================================================================
`windows` Check that :term:`teapot` is currently running on Windows.
`linux`   Check that :term:`teapot` is currently running on Linux.
`darwin`  Check that :term:`teapot` is currently running on Darwin (Mac OS X).
`unix`    Check that :term:`teapot` is currently running on UNIX (Linux or Darwin).
`msvc`    Check that Microsoft Visual Studio is actually available in the current environment.

          It usually means :term:`teapot` was started from a MSVC command shell.
`mingw`   Check that MinGW is available in the current environment.

          The filter will try to find `gcc.exe`.
========= ====================================================================================

.. note::

    When defining several :term:`filters<filter>` in an :term:`attendee`, a :term:`source` or a :term:`builder`, note that **all** filters must be verified for the validation to pass.

You may also define your own filters, see :ref:`extension_modules`.

.. _extensions:

Extensions
----------

Extensions are simple functions, that optionally have parameters, which can occur in a :term:`builder` command.

For instance the `prefix` extension is resolved at runtime and replaced with the complete prefix (as defined at the root of the :term:`party file`, the :term:`attendee` and the :term:`builder`).

Here is an example:

.. code-block:: yaml

    attendees:
      libiconv:
        source: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz
        builders:
          default_x86:
            filters: mingw
            commands:
              - ./configure --prefix={{prefix(unix)}}
              - make
              - make install
            prefix: True

In this example, designed to run from within a MSys environment on Windows, we make use of the `prefix` extension and we supply the `style` parameter. Upon runtime, the expression gets replaced with the UNIX-style path to the prefix, as defined in the :term:`party file`.

Valid syntaxes for calling extensions within commands are:

.. code-block:: yaml

    {{extension}}             # No parameters.
    {{extension()}}           # No parameters. No difference with the first call.
    {{extension(arg1)}}       # Call with one parameter.
    {{extension(arg1,arg2)}}  # Call with two parameters.
    {{extension(,arg2)}}      # Call with two parameters, the first one being omitted.
    {{extension(arg1,,arg3)}} # Call with three parameters, the second one being omitted.

*tea-party* comes with several built-in extensions:

========================== ======================== =====================================================================================================================================
Extension                  Parameters               Role
========================== ======================== =====================================================================================================================================
`prefix`                   style                    Get the complete prefix for the current attendee/builder.

                                                    Returns the complete path, in an operating system specific manner.

                                                    On UNIX and its derivatives, forward slashes are used. On Windows, backwards slashes are used.

                                                    If `style` is set to ``unix``, forward slashes are used, even on Windows. This is useful inside MSys or Cygwin environments.
`prefix_for`               attendee, builder, style Get the complete prefix for the specified attendee/builder.

                                                    You must at least specify the `attendee` parameter.

                                                    Returns the complete path, in an operating system specific manner.

                                                    On UNIX and its derivatives, forward slashes are used. On Windows, backwards slashes are used.

                                                    If `style` is set to ``unix``, forward slashes are used, even on Windows. This is useful inside MSys or Cygwin environments.
`current_attendee`                                  Returns the current attendee name.
`current_builder`                                   Returns the current builder name.
`current_archive_path`     style                    Returns the current archive path.

                                                    On UNIX and its derivatives, forward slashes are used. On Windows, backwards slashes are used.

                                                    If `style` is set to ``unix``, forward slashes are used, even on Windows. This is useful inside MSys or Cygwin environments.
`current_source_tree_path` style                    Returns the current source tree path.

                                                    On UNIX and its derivatives, forward slashes are used. On Windows, backwards slashes are used.

                                                    If `style` is set to ``unix``, forward slashes are used, even on Windows. This is useful inside MSys or Cygwin environments.

                                                    Since source trees are copied to a temporary location before the build, this is **not** the path were the build actually takes place.
========================== ======================== =====================================================================================================================================

You may also define your own extensions, see :ref:`extension_modules`.

Other settings
--------------

:term:`teapot` runs with the following defaults:

============ ======================================= ======================================================================================================
Parameter    Default value                           Meaning
============ ======================================= ======================================================================================================
`cache_path` ``~/.tea-party.cache`` (UNIX)           The path where the archives are downloaded to.

             ``%APPDATA%/tea-party/cache`` (Windows)
`build_path` ``~/.tea-party.build`` (UNIX)           The path where the builds take place.

             ``%APPDATA%/tea-party/build`` (Windows)
`prefix`     ``install``                             The default :term:`party file` prefix that gets prepended to all :term:`attendees<attendee>` prefixes.
============ ======================================= ======================================================================================================

These settings are to be set at the root of the :term:`party file`, like so:

.. code-block:: yaml

    attendees:
      libiconv:
        source: http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz

    cache_path: cache
    build_path: build

Depending on your project, you may want to set the `cache_path` to a more local location (you may choose to add them to version control for instance).

.. _extension_modules:

Writing extension modules
-------------------------

*tea-party* was designed from the start to be extensible.

Using the `extension_modules` attribute at the root of :term:`party file`, you can extend *tea-party* any way you want.

Those extensions modules are regular Python modules into which you can define :term:`filters<filter>`, :term:`extensions<extension>`, :term:`environments<environment>` or anything else you want.

The `extension_modules` attribute is a dictionary located at the root of the :term:`party file` where keys are the shortnames for the modules, and the values are the path to those modules:

.. code-block:: yaml

    extension_modules:
      myfilter: modules/myfilter.py
      myenvironment: modules/myenvironment.py

To get more details about how to write filters, extensions and environments, take a look at :doc:`inside_the_party`.

Using :term:`teapot`
====================

:term:`teapot` is the command line tool that ships with *tea-party*.

.. code-block:: bash

    $ teapot --help
    usage: teapot [-h] [-d] [-v] [-p PARTY_FILE]
                  {clean,fetch,unpack,build} ...

    Manage third-party software.

    positional arguments:
      {clean,fetch,unpack,build}
                            The available commands.
        clean               Clean the party.
        fetch               Fetch all the archives.
        unpack              Unpack all the fetched archives.
        build               Build the archives.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug output.
      -v, --verbose         Be more explicit about what happens.
      -p PARTY_FILE, --party-file PARTY_FILE
                            The party-file to read.

By default, :term:`teapot` looks for a file named ``party.yaml`` in the current directory. You may change the location of this file by using the ``--party-file`` option.

The `clean` command
-------------------

:term:`teapot` fetches the sources archives and stores them in the `cache` directory. It also build attendees and stores the temporary results inside the `build` directory.

Use ``teapot clean`` to clean either the `cache` or the `build` directory (or both).

The use of this command in normally not needed as `tea-party` knows how to compute dependencies and detect changes automatically.

.. code-block:: bash

    $ teapot clean --help
    usage: teapot clean [-h] {cache,build,all} ...

    positional arguments:
      {cache,build,all}  The available commands.
        cache            Clean the party cache.
        build            Clean the party build.
        all              Clean the party cache and build.

    optional arguments:
      -h, --help         show this help message and exit

The `clean cache` command
+++++++++++++++++++++++++

Cleans the *tea-party* cache directory, where the source archives are stored.

Use this command if, for whatever reason you think the archive cache was corrupted.

If no `attendee` is specified, all the attendees are cleaned.

.. code-block:: bash

    $ teapot clean cache --help
    usage: teapot clean cache [-h] [attendee [attendee ...]]

    positional arguments:
      attendee    The attendees to clean.

    optional arguments:
      -h, --help  show this help message and exit

The `clean build` command
+++++++++++++++++++++++++

Cleans the *tea-party* build directory, where the build results are stored.

Use this command if, for whatever reason you think the build results were corrupted.

If no `attendee` is specified, all the attendees are cleaned.

.. code-block:: bash

    $ teapot clean build --help
    usage: teapot clean build [-h] [attendee [attendee ...]]

    positional arguments:
      attendee    The attendees to clean.

    optional arguments:
      -h, --help  show this help message and exit

The `clean cache` command
+++++++++++++++++++++++++

Cleans the *tea-party* cache and build directories.

Use this command if, for whatever reason you want to reset the status of your current *tea-party* project.

If no `attendee` is specified, all the attendees are cleaned.

.. code-block:: bash

    $ teapot clean all --help
    usage: teapot clean all [-h] [attendee [attendee ...]]

    positional arguments:
      attendee    The attendees to clean.

    optional arguments:
      -h, --help  show this help message and exit

The `fetch` command
-------------------

Fetches the source archives of the specified :term:`attendees<attendee>`.

``teapot fetch`` makes sure all the source archives are downloaded for the specified attendees.

If no `attendee` is specified, the source archives for all :term:`attendees<attendee>` are fetched.

By default, this command only fetches archives that weren't already downloaded. Use the ``--force`` option to force the download of all :term:`attendees<attendee>`.

.. code-block:: bash

    $ teapot fetch --help
    usage: teapot fetch [-h] [-f] [attendee [attendee ...]]

    positional arguments:
      attendee     The attendees to fetch.

    optional arguments:
      -h, --help   show this help message and exit
      -f, --force  Fetch archives even if they already exist in the cache.

The `unpack` command
--------------------

Unpacks the fetched source archive to prepare for a build.

If no `attendee` is specified, all the attendees are unpacked.

.. code-block:: bash

    $ teapot unpack --help
    usage: teapot unpack [-h] [-f] [attendee [attendee ...]]

    positional arguments:
      attendee     The attendees to unpack.

    optional arguments:
      -h, --help   show this help message and exit
      -f, --force  Unpack archives even if they already exist in the build.

This step is usually not required as it performed automatically whenever needed. Use it when you don't want to build right away but want the next build to be as fast as possible.

Calling `unpack` automatically fetches the source archives if they are not present.

The `build` command
-------------------

Builds the attendees.

If no `attendee` is specified, all the attendees are built. If a list of `attendees<attendee>` is specified, only those attendees and the ones they depend on will be built.

.. code-block:: bash

    $ teapot build --help
    usage: teapot build [-h] [-t tag] [-u] [-f] [-k] [attendee [attendee ...]]

    positional arguments:
      attendee            The attendees to build.

    optional arguments:
      -h, --help          show this help message and exit
      -t tag, --tags tag  The tags to build.
      -u, --force-unpack  Delete and reunpack all source tree directories before
                          attempting a build.
      -f, --force-build   Run all builders even if their last run was successful.
      -k, --keep-builds   Keep the build directories for inspection.

By default, all variants from all builders are taken. You may specify the ``--tags`` option to build only specific variants (like `x86` or `x64` for instance).

Only the builders that didn't succeeded the last time or the one that changed since the last build are run. To change that behavior, specify the ``--force-build`` option.

**tea-party** will not try to re-unpack archives that were already unpacked unless ``--force-unpack`` is specified.

Temporary build directories are deleted automatically whenever a build terminates (either with a success or a failure), unless the ``--keep-builds`` option is specified. In that case, the build directory remains until the build gets restarted.
