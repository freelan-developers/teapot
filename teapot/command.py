"""
A command class.
"""

import re

from .error import TeapotError
from .filters import FilteredObject
from .signature import SignableObject
from .extensions import parse_extension


class Command(FilteredObject, SignableObject):
    """
    A command.
    """

    signature_fields = ('command', 'filter')

    def __init__(self, command, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.command = command

    def __str__(self):
        return self.command

    def resolve(self, context):
        """
        Apply the extensions to the command.
        """

        def replace(match):
            extension, args, kwargs = parse_extension(match.group('extension'))
            return extension(context, *args, **kwargs)

        return re.sub(r'\{{(?P<extension>([^}]|[}][^}])+)}}', replace, self.command)
