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

Fetchers
========

Unpackers
=========

Party post-actions
==================
