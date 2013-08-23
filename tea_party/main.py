"""
The tea-party main script.
"""

import os
import sys
import argparse
import logging

from functools import wraps

from tea_party.log import LOGGER
from tea_party.party import load_party_file
from tea_party.fetchers.callbacks import ProgressBarFetcherCallback


def main():
    """
    The script entry point.
    """

    parser = argparse.ArgumentParser(
        description='Manage third-party software.'
    )

    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output.')

    command_parser = parser.add_subparsers(help='The available commands.')
    parser.add_argument('-p', '--party-file', default=None, help='The party-file to read.')

    # The clean command
    clean_command_parser = command_parser.add_parser('clean', help='Clean the party cache.')
    clean_command_parser.set_defaults(func=clean)
    clean_command_parser.add_argument('attendee', nargs='?', help='The attendee to clean.')

    # The fetch command
    fetch_command_parser = command_parser.add_parser('fetch', help='Fetch all the archives.')
    fetch_command_parser.set_defaults(func=fetch)
    fetch_command_parser.add_argument('-f', '--force', action='store_true', help='Fetch archives even if they already exist in the cache.')

    # The unpack command
    unpack_command_parser = command_parser.add_parser('unpack', help='Unpack all the fetched archives.')
    unpack_command_parser.set_defaults(func=unpack)
    unpack_command_parser.add_argument('-f', '--force', action='store_true', help='Unpack archives even if they already exist in the build.')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
        logging.getLogger('requests').setLevel(logging.WARNING)

    if args.party_file is None:
        args.party_file = os.path.join(os.getcwd(), 'party.yaml')

    try:
        party = load_party_file(args.party_file)

    except IOError:
        LOGGER.error('No party-file was found. (Searched path: "%s")', args.party_file)

        return 1

    context = {
        'fetcher_callback_class': ProgressBarFetcherCallback,
    }

    if not args.func(party, context, args):
        return 2

def command(func):
    """
    Provides exception handling for commands.
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            func(*args, **kwargs)

            return True
        except Exception as ex:
            LOGGER.exception(ex)

            return False

    return decorated

@command
def clean(party, context, args):
    """
    Clean the party.
    """

    party.clean_cache(
        attendee=args.attendee,
    )

@command
def fetch(party, context, args):
    """
    Fetch the archives.
    """

    party.fetch(
        force=args.force,
        context=context,
    )

@command
def unpack(party, context, args):
    """
    Unpack the archives.
    """

    party.unpack(
        force=args.force,
        context=context,
    )
