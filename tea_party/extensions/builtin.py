"""
Built-in extensions.
"""

import os
import sys

from tea_party.path import windows_to_unix_path
from tea_party.extensions.decorators import named_extension


@named_extension('prefix')
def prefix(builder, style='default'):
    """
    Get the builder prefix.
    """

    result = os.path.join(builder.attendee.party.prefix, builder.attendee.prefix, builder.prefix)

    if sys.platform.startswith('win32') and style == 'unix':
        result = windows_to_unix_path(result)

    return result
