"""
Built-in extensions.
"""

import os
import sys
import subprocess

from functools import wraps

from ..path import windows_to_unix_path
from ..path import resolve_user_path
from ..options import get_option
from ..attendee import Attendee

from .extension import register_extension


def styleable(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        style = kwargs.pop('style', None)
        result = func(*args, **kwargs)

        if sys.platform.startswith('win32') and style == 'unix':
            result = windows_to_unix_path(result)

        return result

    return wrapped_func


@register_extension('root')
@styleable
@resolve_user_path
def root(build):
    """
    Get the build prefix.
    """

    return os.path.dirname(build.attendee.party_path)


@register_extension('prefix')
@styleable
@resolve_user_path
def prefix(build):
    """
    Get the build prefix.
    """

    return os.path.join(
        build.apply_extensions(get_option('prefix')),
        build.apply_extensions(build.attendee.prefix),
        build.apply_extensions(build.prefix),
    )


@register_extension('prefix_for')
@styleable
@resolve_user_path
def prefix_for(build, attendee, attendee_build=None):
    """
    Get the build prefix for a given attendee, and optionally one of its builders.
    """

    attendee = Attendee.get_instance_or_fail(attendee)
    attendee_build_prefix = attendee.get_build(attendee_build).prefix if attendee_build is not None else ''

    return os.path.join(
        build.apply_extensions(get_option('prefix')),
        build.apply_extensions(attendee.prefix),
        build.apply_extensions(attendee_build_prefix),
    )


@register_extension('attendee')
def attendee(build):
    """
    Get the current attendee.
    """

    return build.attendee


@register_extension('build')
def build(build):
    """
    Get the current build.
    """

    return build.name


@register_extension('full_build')
def full_build(build):
    """
    Get the full current build.
    """

    return build


@register_extension('archive_path')
@styleable
@resolve_user_path
def archive_path(build):
    """
    Get the current archive path.
    """

    return build.attendee.archive_path


@register_extension('extracted_sources_path')
@styleable
@resolve_user_path
def extracted_sources_path(build):
    """
    Get the current source tree path.
    """

    return build.attendee.extracted_sources_path


@register_extension('msvc_version')
def msvc_version(builder):
    """
    Get the MSVC version.
    """

    return os.environ.get('VisualStudioVersion')


@register_extension('msvc_toolset')
def msvc_toolset(builder):
    """
    Get the MSVC toolset.
    """

    version = msvc_version(builder)

    toolset_map = {
        '12.0': 'v120',
        '11.0': 'v110',
    }

    return toolset_map.get(version)
