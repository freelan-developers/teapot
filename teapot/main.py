"""
The teapot main script.
"""

import os
import sys
import argparse
import logging
import traceback

from functools import wraps

from .log import LOGGER, ColorizingStreamHandler
from .error import TeapotError
from .path import chdir

import teapot.party


def main():
    """
    The script entry point.
    """

    parser = argparse.ArgumentParser(
        description='Manage third-party software.'
    )

    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug output.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Be more explicit about what happens.')

    command_parser = parser.add_subparsers(help='The available commands.')
    parser.add_argument('-p', '--party-file', default=None,
                        help='The party-file to read.')

    # The clean command
    clean_command_parser = command_parser.add_parser(
        'clean', help='Clean the party.')
    clean_subcommand_parser = clean_command_parser.add_subparsers(
        help='The available commands.')

    #  The clean cache subcommand
    clean_cache_command_parser = clean_subcommand_parser.add_parser(
        'cache', help='Clean the party cache.')
    clean_cache_command_parser.set_defaults(func=clean_cache)
    clean_cache_command_parser.add_argument(
        'attendees', metavar='attendee', nargs='*', default=[], help='The attendees to clean.')

    #  The clean sources subcommand
    clean_sources_command_parser = clean_subcommand_parser.add_parser(
        'sources', help='Clean the party sources.')
    clean_sources_command_parser.set_defaults(func=clean_sources)
    clean_sources_command_parser.add_argument(
        'attendees', metavar='attendee', nargs='*', default=[], help='The attendees to clean.')

    #  The clean build subcommand
    clean_build_command_parser = clean_subcommand_parser.add_parser(
        'build', help='Clean the party build.')
    clean_build_command_parser.set_defaults(func=clean_build)
    clean_build_command_parser.add_argument(
        'attendees', metavar='attendee', nargs='*', default=[], help='The attendees to clean.')

    #  The clean install subcommand
    clean_install_command_parser = clean_subcommand_parser.add_parser(
        'install', help='Clean the party install.')
    clean_install_command_parser.set_defaults(func=clean_install)
    clean_install_command_parser.add_argument(
        'attendees', metavar='attendee', nargs='*', default=[], help='The attendees to clean.')

    #  The clean all subcommand
    clean_all_command_parser = clean_subcommand_parser.add_parser(
        'all', help='Clean the party cache, build and install.')
    clean_all_command_parser.set_defaults(func=clean_all)
    clean_all_command_parser.add_argument(
        'attendees', metavar='attendee', nargs='*', default=[], help='The attendees to clean.')

    # The fetch command
    fetch_command_parser = command_parser.add_parser(
        'fetch', help='Fetch all the archives.')
    fetch_command_parser.set_defaults(func=fetch)
    fetch_command_parser.add_argument(
        'attendees', metavar='attendee', nargs='*', default=[], help='The attendees to fetch.')
    fetch_command_parser.add_argument(
        '-f', '--force', action='store_true', help='Fetch archives even if they already exist in the cache.')

    # The unpack command
    unpack_command_parser = command_parser.add_parser(
        'unpack', help='Unpack all the fetched archives.')
    unpack_command_parser.set_defaults(func=unpack)
    unpack_command_parser.add_argument(
        'attendees', metavar='attendee', nargs='*', default=[], help='The attendees to unpack.')
    unpack_command_parser.add_argument(
        '-f', '--force', action='store_true', help='Unpack archives even if they already exist in the build.')

    # The build command
    build_command_parser = command_parser.add_parser(
        'build', help='Build the archives.')
    build_command_parser.set_defaults(func=build)
    build_command_parser.add_argument(
        'attendees', metavar='attendee', nargs='*', default=[], help='The attendees to build.')
    build_command_parser.add_argument(
        '-f', '--force', action='store_true', help='Fetch archives even if they already exist in the cache.')
    build_command_parser.add_argument(
        '-k', '--keep-builds', action='store_true', help='Keep the build directories for inspection.')

    args = parser.parse_args()

    handler = ColorizingStreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    if args.debug:
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.INFO)

    if args.party_file is None:
        args.party_file = os.path.join(os.getcwd(), 'Party')
    else:
        args.party_file = os.path.abspath(args.party_file)

    with chdir(os.path.dirname(args.party_file)):
        try:
            teapot.party.load_party_file(args.party_file)

        except IOError:
            LOGGER.error(
                'No party-file was found. (Searched path: "%s")',
                args.party_file,
            )

            return 1

        if not args.func(args):
            return 2


def command(func):
    """
    Provides exception handling for commands.
    """

    @wraps(func)
    def decorated(args, **kwargs):
        try:
            func(args, **kwargs)

            return True

        except KeyboardInterrupt:
            pass

        except TeapotError as ex:
            LOGGER.error(ex.msg, *ex.args)

            if args.debug:
                LOGGER.debug('\nTraceback is:\n' + ''.join(traceback.format_tb(sys.exc_info()[2])))

        except Exception as ex:
            if args.debug:
                LOGGER.exception(ex)
            else:
                LOGGER.error(str(ex))

        LOGGER.error('teapot execution failed.')

        return False

    return decorated


@command
def clean_cache(args):
    """
    Clean the party cache.
    """

    teapot.party.clean_cache(
        attendees=args.attendees,
    )


@command
def clean_sources(args):
    """
    Clean the party sources.
    """

    teapot.party.clean_sources(
        attendees=args.attendees,
    )


@command
def clean_build(party, args):
    """
    Clean the party build.
    """

    teapot.party.clean_build(
        attendees=args.attendees,
    )


@command
def clean_install(party, args):
    """
    Clean the party install.
    """

    teapot.party.clean_install(
        attendees=args.attendees,
    )


@command
def clean_all(args):
    """
    Clean the party cache and build.
    """

    teapot.party.clean_all(
        attendees=args.attendees,
    )


@command
def fetch(args):
    """
    Fetch the archives.
    """

    teapot.party.fetch(
        attendees=args.attendees,
        force=args.force,
    )


@command
def unpack(args):
    """
    Unpack the archives.
    """

    teapot.party.unpack(
        attendees=args.attendees,
        force=args.force,
    )


@command
def build(args):
    """
    Build the archives.
    """

    teapot.party.build(
        attendees=args.attendees,
        force=args.force,
        verbose=args.verbose,
        keep_builds=args.keep_builds,
    )
