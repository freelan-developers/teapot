"""
3party 'party' class.
"""

import yaml

def load_party(path):
    """
    Load a party file from a path.
    """

    with open(path) as fs:
        data = fs.read()

    values = yaml.load(data)

    return Party(**values)

class Party(object):
    """
    Parses and manages 3party 'party' files.

    A 'party' file is a regular YAML files containing 3party specific options.
    """

    def __init__(self, attendees, **kwargs):
        """
        Creates a new Party.
        """

        self.attendees = attendees
