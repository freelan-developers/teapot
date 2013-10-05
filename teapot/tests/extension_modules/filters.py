"""
Some test filters.
"""

from teapot.filters.decorators import named_filter

@named_filter('true_filter')
def true_filter():
    """
    Returns true.
    """

    return True

@named_filter('false_filter')
def false_filter():
    """
    Returns false.
    """

    return False
