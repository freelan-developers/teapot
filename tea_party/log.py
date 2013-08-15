"""
The tea-party logging facilities.
"""

import logging


LOGGER = logging.getLogger('tea-party')
LOGGER.addHandler(logging.NullHandler())
