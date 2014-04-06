"""
The built-in filters.
"""

import os
import sys
import distutils
import subprocess

from .filter import named_filter


@named_filter('windows')
def windows():
    """
    Check if the platform is windows.
    """

    return sys.platform.startswith('win32')


@named_filter('linux')
def linux():
    """
    Check if the platform is windows.
    """

    return sys.platform.startswith('linux')


@named_filter('darwin')
def darwin():
    """
    Check if the platform is darwin.
    """

    return sys.platform.startswith('darwin')


@named_filter('unix')
def unix():
    """
    Check if the platform is unix.
    """

    return linux() or darwin()


@named_filter('msvc', depends_on='windows')
def msvc():
    """
    Check if MSVC is available.
    """

    return 'VCINSTALLDIR' in os.environ


@named_filter('msvc-x86', depends_on='msvc')
def msvc_x86():
    """
    Check if MSVC x86 is available.
    """

    output = subprocess.check_output(
        'cl.exe', shell=True, stderr=subprocess.STDOUT)
    first_line = output.split('\n')[0].rstrip()

    return 'x86' in first_line


@named_filter('msvc-x64', depends_on='msvc')
def msvc_x64():
    """
    Check if MSVC x64 is available.
    """

    output = subprocess.check_output(
        'cl.exe', shell=True, stderr=subprocess.STDOUT)
    first_line = output.split('\n')[0].rstrip()

    return 'x64' in first_line


@named_filter('mingw', depends_on='windows')
def mingw():
    """
    Check if MinGW is available.
    """

    return bool(distutils.spawn.find_executable('gcc'))
