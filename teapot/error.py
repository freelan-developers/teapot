"""
A teapot error class.
"""


class TeapotError(RuntimeError):

    """
    Represents a runtime teapot-specific error.
    """

    def __init__(self, msg, *args):
        self.msg = msg
        self.msg_args = args

    def __str__(self):
        return self.msg % self.msg_args
