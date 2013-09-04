"""
The tea-party logging facilities.
"""

import sys
import logging
import colorama


LOGGER = logging.getLogger('tea-party')
LOGGER.addHandler(logging.NullHandler())

# Add new log levels
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

# Extend the LogRecord class getMessage() method to support highlighting
logging.LogRecord.getLegacyMessage = logging.LogRecord.getMessage

def getMessage(self):
    """
    Return the message from this LogRecord.
    """

    colorizer = getattr(self, 'colorizer', None)

    if colorizer:
        self.args = tuple(map(colorizer, self.args))

    return self.getLegacyMessage()

logging.LogRecord.getMessage = getMessage

class Highlight(object):
    """
    Highlight an instance in the logs.
    """

    def __init__(self, msg):
        """
        Create a highlight object.
        """

        self.msg = msg

    def __str__(self):
        """
        Return a string representation.
        """

        return str(self.msg)

    def render(self, color, reset):
        """
        Return a colorized representation.
        """

        return '%s%s%s' % (color, self.msg, reset)

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

        if self.is_tty:
            highlight_color = self.COLOR_MAP.get(logging.IMPORTANT)
            log_color = self.COLOR_MAP.get(record.levelno, '')
            reset = colorama.Style.RESET_ALL

            def colorize(msg):

                if isinstance(msg, Highlight):
                    return msg.render(
                        color=highlight_color,
                        reset=reset + log_color,
                    )

                return msg

            record.colorizer = colorize

        message = super(ColorizingStreamHandler, self).format(record)

        if self.is_tty:
            message = '%s%s%s' % (log_color, message, reset)

        return message
