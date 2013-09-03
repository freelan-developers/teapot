"""
The tea-party logging facilities.
"""

import re
import sys
import logging
import colorama


LOGGER = logging.getLogger('tea-party')
LOGGER.addHandler(logging.NullHandler())

def register_log_level(name, value):
    """
    Register a new log level.
    """

    setattr(logging, name.upper(), value)
    logging.addLevelName(value, name.upper())

    def log_func(self, message, *args, **kwargs):
        self._log(value, message, args, **kwargs)

    setattr(logging.Logger, name, log_func)

register_log_level('important', logging.INFO + 1)
register_log_level('success', logging.INFO + 2)

def hl(msg):
    """
    Returns a highlighted version of `msg`.
    """

    return '<[{%s}]>' % msg

def print_normal(msg):
    """
    Print a normal line.
    """

    sys.stdout.write(colorama.Fore.BLUE + msg + colorama.Style.RESET_ALL)

def print_error(msg):
    """
    Print an error line.
    """

    sys.stdout.write(colorama.Fore.RED + msg + colorama.Style.RESET_ALL)

class ColorizingStreamHandler(logging.StreamHandler):
    """
    A logging handler that colorizes its output.
    """

    COLOR_MAP = {
        logging.DEBUG: colorama.Style.DIM + colorama.Fore.CYAN,
        logging.IMPORTANT: colorama.Style.BRIGHT,
        logging.SUCCESS: colorama.Fore.GREEN,
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
            highlight_color = self.COLOR_MAP.get(logging.IMPORTANT)
            color = self.COLOR_MAP.get(record.levelno, '')
            reset = colorama.Style.RESET_ALL
            message = re.sub('<\[\{(.*?)\}\]>', lambda m: highlight_color + m.group(1) + reset + color, message)
            message = '%s%s%s' % (color, message, reset)
        else:
            message = re.sub('<\[\{(.*?)\}\]>', lambda m: m.group(1), message)

        return message
