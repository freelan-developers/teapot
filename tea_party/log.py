"""
The tea-party logging facilities.
"""

import re
import logging


LOGGER = logging.getLogger('tea-party')
LOGGER.addHandler(logging.NullHandler())

logging.IMPORTANT = logging.INFO + 1
logging.SUCCESS = logging.IMPORTANT + 1
logging.addLevelName(logging.IMPORTANT, 'IMPORTANT')
logging.addLevelName(logging.SUCCESS, 'SUCCESS')

def important(self, message, *args, **kwargs):
    """
    Outputs an important log.
    """

    self._log(logging.IMPORTANT, message, args, **kwargs)

def success(self, message, *args, **kwargs):
    """
    Outputs a success log.
    """

    self._log(logging.SUCCESS, message, args, **kwargs)

logging.Logger.important = important
logging.Logger.success = success

try:
    import colorama

    def highlighted(msg):
        """
        Returns a highlighted version of `msg`.
        """

        return '<[{%s}]>' % msg

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

except ImportError:

    def highlighted(msg):
        """
        Returns a highlighted version of `msg`.
        """

        return msg

    ColorizingStreamHandler = logging.StreamHandler
