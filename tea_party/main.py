"""
The tea-party main script.
"""

import os
import sys
import argparse
import logging

from tea_party.party import load_party_file
from tea_party.fetchers.callbacks import ProgressBarFetcherCallback


LOGGER = logging.getLogger('tea_party.main')

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

    # The status command
    status_command_parser = command_parser.add_parser('status', help='Get the party status.')

    # The fetch command
    fetch_command_parser = command_parser.add_parser('fetch', help='Fetch all the archives.')
    fetch_command_parser.set_defaults(func=fetch)
    fetch_command_parser.add_argument('-f', '--force', action='store_true', help='Fetch archives even if they exist already in the cache.')

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

def fetch(party, context, args):
    """
    Fetch the archives.
    """

    return party.fetch(
        force=args.force,
        context=context,
    )
