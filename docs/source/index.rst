tea-party - A third-party building tool
***************************************

This documentation is about **tea-party**, a multi-platform tool to ease fetching, organization and building of third-party softwares.

What is **tea-party** ?
=======================

**tea-party** is a Python package that comes with `teapot`, a command-line interface tool. `teapot` reads a YAML file (called the *party file*) which defines the source, the properties, the environment and the build steps for all the third-party libraries to build.

The idea is to add a simple ``party.yaml`` file inside your project source tree that will describe which third-party libraries it depends on and how to build them.

The first chapter, :doc:`the_party_file`, describes the format of the :term:`party file` and enumerates all the possible options.

The second chapter, :doc:`inside_the_party`, explains the internals of the :mod:`tea_party` module, which will allow you to easily write custom filters, extensions, fetchers, unarchivers and to change the complete behavior of **tea-party** to perfectly suit your needs.

Why should I use **tea-party** ?
================================

Because you probably have more interesting things to do that dealing with third-party softwares.

Most of the time, people and companies end up writing their own set of scripts to build their dependencies. It can go from a simple `wget` call that fetches precompiled binaries from some server, to more complex systems that download and build them from source and try to do so as reliably as they can.

Writing a script that downloads a `.tar.gz` file, uncompresses it and builds it is really not difficult. But what if you want to handle dependencies between your third party libraries, or desire to support variant builds ? How do you deal with multiple platforms ? How can you react to changes and automatically rebuild what's necessary ? With **tea-party**, you just have to write a simple *party file* once and call the `teapot` command once in a while. You can even integrate it into your usual build system since it automatically deals with dependencies and avoids unecessary rebuilds.

How simpler can it get ?

So, will *tea-party* build my third-party software for me ?
===========================================================

Yes it will, but you will still have to tell him how exactly.

There are just too many different ways of building software for this to be done without human guidance.

However, *tea-party* will make this as painless as it can get by automating all the other things that can be automated.

Why this name ?
===============

No good reason really. I just don't like spending too much time finding catchy names and *tea-party* sort-of sounds like *third-party*.

It has **nothing** to do with the american politic movement "The Tea Party".

What's next ?
=============

Here are the chapters you should read if you want to get familiar with *tea-party*:

.. toctree::
   :maxdepth: 2
   :numbered:

   the_party_file
   inside_the_party
   glossary
