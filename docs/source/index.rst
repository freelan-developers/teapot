tea-party - A third-party building tool
***************************************

This documentation is about **tea-party**, a multi-platform tool to ease fetching, organization and building of third-party softwares.

What is **tea-party** ?
=======================

**tea-party** is a Python package that comes with `teapot`, a command-line interface tool. `teapot` reads a YAML file (called the *party file*) which defines the source, the properties and the build steps for all third-party libraries to build.

The first chapter, :doc:`the_party_file`, describes the format of the *party file* and enumerates all the possible options.

The second chapter, :doc:`inside_the_party`, explains the internals of the :mod:`tea_party` module, which will allow you to easily write custom filters, extensions, fetchers, unarchivers and to change the complete behavior of **tea-party** to perfectly suit your needs.

Why should I use **tea-party** ?
================================

Because, like all of us, you probably have more interesting things to do that dealing with third-party softwares.

Most of the time, people and companies end up writing their own set of scripts to build their dependencies. It can go from a simple `wget` call that fetches precompiled binaries from some server, to more complex systems that download and build them from source and try to do so as reliably as they can.

Writing a script that downloads a `.tar.gz` file, uncompresses it and builds it is really not difficult. But what if you want to handle dependencies between your third party libraries, or desire to support variant builds ? How do you deal with multiple platforms ? How can you react to changes and automatically rebuild what's necessary ? With **tea-party**, you just have to write a simple *party file* once, call the `teapot` command and be done.

How simpler can it get ?

Why this stupid name ?
======================

No reason really. I just don't like spending too much time finding catchy names.

.. note:: I realized, a bit too late, that "The Tea Party" is also a (famous ?) politic movement in the U.S.A: I absolutely have no idea what they stand for nor do I actually care about it. Unless their goal is to ease the compilation of third-party softwares, we probably have nothing in common.

What's next ?
=============

.. toctree::
   :maxdepth: 2
   :numbered:

   the_party_file
   inside_the_party
