Glossary
********

.. glossary::

    party file
      The party file is a YAML file, named `party.yaml` that can be located anywhere.
      
      Within the party file, all paths are relative to the party file directory.

    attendee
      An attendee is a fancy name for a third-party software to build.
      
      A :term:`party file` can contain as many attendees as you like, and different attendees can even represent the same third-party software if that makes sense in your situation.

    source
      A source designates the location and the method where and how to fetch the source files for an :term:`attendee`. While the most common case is downloading a file using HTTP, one can also copy a file locally, through a network share or from Github.

    fetcher
      A fetcher is the entity that is responsible for handling a specific type of source.
      
      Usually, fetchers are smart enough to recognize sources from their format and you should not have to care too much about them.

    unpacker
      An unpacker is the entity that is responsible for turning a compressed archive (Zip file or tarball for instance) into a source tree.

    builder
      A builder is the list of commands to execute in order to transform the attendee source into a compiled set of binaries (or whatever a build process can produce).
      
      Builders rely a lot on :term:`environments<environment>`.

    environment
      An environment is a set of environment variables, shell value and inheritance parameters that wraps one or several builds.
      
      Environments define the tools to use for a given build, and their options.

    filter
      A filter is an entity whose role is to check if the current execution environment matches a series of criterias.

      For instance, the `windows` filter checks that `teapot` has been run on Windows. Another example is the `mingw` filter whose role is to check that MinGW is currently available in the execution environment.

    teapot
      `teapot` is the name of the command-line tool that implements all tea-party logic.

    shell
      A shell is a command line interpreter that will execute the different commands of a builder.

    extension
      An extension is an entity the resides in builder commands and that gets replaced when the command is evaluated.

      Extension are python function that can optionally take parameters.
