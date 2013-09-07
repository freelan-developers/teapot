"""
Built-in extensions.
"""

from tea_party.extensions.decorators import named_extension


@named_extension('prefix')
def prefix(builder):
    """
    Get the builder prefix.
    """

    return builder.prefix
