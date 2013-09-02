"""
The tea-party logging facilities.
"""

import logging


LOGGER = logging.getLogger('tea-party')
LOGGER.addHandler(logging.NullHandler())

try:
    import colorama

    class ColorizingStreamHandler(logging.StreamHandler):
        """
        A logging handler that colorizes its output.
        """

        COLOR_MAP = {
            logging.DEBUG: colorama.Style.DIM + colorama.Fore.CYAN,
            logging.WARNING: colorama.Fore.YELLOW,
            logging.ERROR: colorama.Fore.RED,
            logging.CRITICAL: colorama.Back.RED,
        }

        def __init__(self, stream):
            super(ColorizingStreamHandler, self).__init__(
                colorama.AnsiToWin32(stream).stream,
            )

        @property
        def is_tty(self):
            """
            Check if we are in a tty.
            """

            return getattr(self.stream, 'isatty', lambda: False)()

        def format(self, record):
            """
            Format a record.
            """

            message = super(ColorizingStreamHandler, self).format(record)

            if self.is_tty:
                message = '%s%s%s' % (self.COLOR_MAP.get(record.levelno, ''), message, colorama.Style.RESET_ALL)

            return message

except ImportError:
    ColorizingStreamHandler = logging.StreamHandler
