"""
Built-in extensions.
"""

import os
import sys

from teapot.path import windows_to_unix_path
from teapot.extensions.decorators import named_extension


@named_extension('root')
def root(builder, style='default'):
    """
    Get the builder prefix.
    """

    result = os.path.dirname(builder.attendee.party.path)

    if sys.platform.startswith('win32') and style == 'unix':
        result = windows_to_unix_path(result)

    return result

@named_extension('prefix')
def prefix(builder, style='default'):
    """
    Get the builder prefix.
    """

    result = os.path.join(builder.attendee.party.prefix, builder.attendee.prefix, builder.prefix)

    if sys.platform.startswith('win32') and style == 'unix':
        result = windows_to_unix_path(result)

    return result

@named_extension('prefix_for')
def prefix_for(builder, for_attendee, for_builder='', style='default'):
    """
    Get the builder prefix for a given attendee, and optionally one of its builders.
    """

    party = builder.attendee.party

    for_attendee = party.get_attendee_by_name(for_attendee)
    builder_prefix = attendee.get_builder_by_name(for_builder).prefix if for_builder else ''

    result = os.path.join(party.prefix, attendee.prefix, builder_prefix)

    if sys.platform.startswith('win32') and style == 'unix':
        result = windows_to_unix_path(result)

    return result

@named_extension('current_attendee')
def current_attendee(builder):
    """
    Get the current attendee.
    """

    return builder.attendee

@named_extension('current_builder')
def current_builder(builder):
    """
    Get the current builder.
    """

    return builder

@named_extension('current_archive_path')
def current_archive_path(builder, style='default'):
    """
    Get the current archive path.
    """

    result = builder.attendee.archive_path

    if sys.platform.startswith('win32') and style == 'unix':
        result = windows_to_unix_path(result)

    return result

@named_extension('current_source_tree_path')
def current_source_tree_path(builder, style='default'):
    """
    Get the current source tree path.
    """

    result = builder.attendee.source_tree_path

    if sys.platform.startswith('win32') and style == 'unix':
        result = windows_to_unix_path(result)

    return result
