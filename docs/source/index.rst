teapot - A third-party building tool
***************************************

This documentation is about **teapot**, a multi-platform tool to ease fetching, organization and building of third-party softwares.

What is **teapot** ?
=======================

**teapot** is a Python package that comes with `teapot`, a command-line interface tool. `teapot` reads a party file which defines the source, the properties, the environment and the build steps for all the third-party libraries to build.

The idea is to add a simple ``Party`` (or ``.party``) file inside your project source tree that will describe which third-party libraries it depends on and how to build them.

:doc:`the_party_file`, describes the format of the :term:`party file` and enumerates all the possible options.

Why should I use **teapot** ?
================================

Because you probably have more interesting things to do than dealing with third-party softwares.

Most of the time, people and companies end up writing their own set of scripts to build their dependencies. It can go from a simple `wget` call that fetches precompiled binaries from some server, to more complex systems that download and build them from source and try to do so as reliably as they can.

Writing a script that downloads a `.tar.gz` file, uncompresses it and builds it is really not difficult. But what if you want to handle dependencies between your third party libraries, or desire to support variant builds ? How do you deal with multiple platforms ? How can you react to changes and automatically rebuild what's necessary ? With **teapot**, you just have to write a simple *party file* once and call the `teapot` command once in a while. You can even integrate it into your usual build system since it automatically deals with dependencies and avoids unecessary rebuilds.

For instance, this :term:`party file` downloads, unpacks and builds the popular ``libiconv`` on all UNIX platforms:

..  code-block:: python

    from teapot import *
    
    Attendee('iconv').add_source('http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz')
    Attendee('iconv').add_build('default')
    Attendee('iconv').get_build('default').add_command('./configure --prefix={{prefix}}')
    Attendee('iconv').get_build('default').add_command('make')
    Attendee('iconv').get_build('default').add_command('make install')

How simpler can it get ?

So, will *teapot* build my third-party software for me ?
===========================================================

Yes it will, but you will still have to tell him how exactly.

There are just too many different ways of building software for this to be done without human guidance.

However, *teapot* will make this as painless as it can get by automating all the other steps that can be automated.

Why this name ?
===============

No good reason really. I just don't like spending too much time finding catchy names and a *teapot* is a nice object so... why not ? :)

What's next ?
=============

Here are the chapters you should read if you want to get familiar with *teapot*:

.. toctree::
   :maxdepth: 2
   :numbered:

   the_party_file
   glossary
