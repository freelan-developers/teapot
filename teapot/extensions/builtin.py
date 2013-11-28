"""
Built-in extensions.
"""

import os
import sys
import subprocess

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

    result = os.path.join(
        builder.apply_extensions(builder.attendee.party.prefix),
        builder.apply_extensions(builder.attendee.prefix),
        builder.apply_extensions(builder.prefix),
    )

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

    result = os.path.join(
        builder.apply_extensions(party.prefix),
        builder.apply_extensions(attendee.prefix),
        builder.apply_extensions(builder_prefix),
    )

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

@named_extension('msvc_version')
def msvc_version(builder):
    """
    Get the MSVC version.
    """

    version = os.environ.get('VisualStudioVersion')

    if version is None:
      version = '10.0'

    return version

@named_extension('msvc_major_version')
def msvc_major_version(builder):
    """
    Get the MSVC major version.
    """

    version = msvc_version(builder)

    if version is not None:
        major_version = version.split('.')[0]

        return major_version

@named_extension('msvc_toolset')
def msvc_toolset(builder):
    """
    Get the MSVC toolset.
    """

    version = msvc_version(builder)

    toolset_map = {
        '12.0': 'v120',
        '11.0': 'v110',
        '10.0': 'v100',
    }

    return toolset_map.get(version)
