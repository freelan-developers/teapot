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
from ..build import Build

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
def root(context):
    """
    Get party root.
    """

    if isinstance(context, Build):
        return context.attendee.party_root
    elif isinstance(context, Attendee):
        return context.party_root


@register_extension('prefix')
@styleable
@resolve_user_path
def prefix(context):
    """
    Get the prefix.
    """

    if isinstance(context, Build):
        return os.path.join(
            root(context),
            get_option('prefix'),
            context.attendee.prefix,
            context.prefix,
        )
    elif isinstance(context, Attendee):
        return os.path.join(
            root(context),
            get_option('prefix'),
            context.prefix,
        )


@register_extension('prefix_for')
@styleable
@resolve_user_path
def prefix_for(context, attendee, attendee_build=None):
    """
    Get the build prefix for a given attendee, and optionally one of its builders.
    """

    attendee = Attendee.get_instance_or_fail(attendee)
    attendee_build_prefix = attendee.get_build(attendee_build).prefix if attendee_build is not None else ''

    return os.path.join(
        root(context),
        get_option('prefix'),
        attendee.prefix,
        attendee_build_prefix,
    )


@register_extension('attendee')
def attendee(context):
    """
    Get the current attendee.
    """

    if isinstance(context, Build):
        return context.attendee
    elif isinstance(context, Attendee):
        return context


@register_extension('build')
def build(context):
    """
    Get the current build.
    """

    if isinstance(context, Build):
        return context.name


@register_extension('full_build')
def full_build(context):
    """
    Get the full current build.
    """

    if isinstance(context, Build):
        return context.name


@register_extension('archive_path')
@styleable
@resolve_user_path
def archive_path(context):
    """
    Get the current archive path.
    """

    return attendee(context).archive_path


@register_extension('extracted_sources_path')
@styleable
@resolve_user_path
def extracted_sources_path(context):
    """
    Get the current source tree path.
    """

    return attendee(context).extracted_sources_path


@register_extension('msvc_version')
def msvc_version(contexter):
    """
    Get the MSVC version.
    """

    return os.environ.get('VisualStudioVersion')


@register_extension('msvc_toolset')
def msvc_toolset(contexter):
    """
    Get the MSVC toolset.
    """

    version = msvc_version(contexter)

    toolset_map = {
        '12.0': 'v120',
        '11.0': 'v110',
    }

    return toolset_map.get(version)
