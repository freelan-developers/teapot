"""
Extensions implementation.
"""

from lepl import Drop
from lepl import Literal
from lepl import Word
from lepl import Letter
from lepl import Digit
from lepl import Real
from lepl import Integer
from lepl import String
from lepl import Separator
from lepl import Regexp
from lepl import Delayed
from lepl import Eos
from lepl import Node
from lepl.stream.maxdepth import FullFirstMatchException

from ..error import TeapotError
from ..log import LOGGER, Highlight as hl

from .extension import Extension


class ExtensionParser(object):

    """
    A class that parses extensions.
    """

    class ExtensionCall(Node):

        """
        An extension call.
        """

        _name = None
        _args = None
        _kwargs = None

        @property
        def name(self):
            return self._name[0] if self._name else None

        @property
        def args(self):
            return tuple(self._args) if self._args else tuple()

        @property
        def kwargs(self):
            return dict(self._kwargs) if self._kwargs else {}

    COMMA = Drop(',')
    NONE = Literal('None') >> (lambda x: None)
    BOOL = (Literal('True') | Literal('False')) >> (lambda x: x == 'True')
    IDENTIFIER = Word(Letter() | '_', Letter() | '_' | Digit())
    FLOAT = Real() >> float
    INTEGER = Integer() >> int
    STRING = String() | String("'")
    ITEM = STRING | INTEGER | FLOAT | NONE | BOOL | IDENTIFIER

    with Separator(~Regexp(r'\s*')):
        VALUE = Delayed()
        LIST = Drop('[') & VALUE[:, COMMA] & Drop(']') > list
        TUPLE = Drop('(') & VALUE[:, COMMA] & Drop(')') > tuple
        VALUE += LIST | TUPLE | ITEM
        ARGUMENT = VALUE >> '_args'
        KWARGUMENT = (IDENTIFIER & Drop('=') & VALUE > tuple) >> '_kwargs'
        ARGUMENTS = (KWARGUMENT | ARGUMENT)[:, COMMA]
        NAME = IDENTIFIER > '_name'
        EXTENSION = ((NAME & Drop('(') & ARGUMENTS & Drop(')')) | NAME) & Eos() > ExtensionCall

    @property
    def parser(self):
        return self.EXTENSION.get_parse_string()


def parse_extension(extension):
    """
    Parse an extension call and return the appropriate extension call object,
    as well as its parameters.

    Return (extension, args, kwargs).
    """

    try:
        extension_node = ExtensionParser().parser(extension)[0]
    except FullFirstMatchException as ex:
        raise TeapotError("Unable to parse the extension %r. Error was: %s", hl(extension), hl(str(ex)))

    return (
        Extension.get_instance_or_fail(extension_node.name),
        extension_node.args,
        extension_node.kwargs,
    )
