"""
Provides tools to deal with third-party software.
"""

import teapot.filters.builtin
import teapot.extensions.builtin

from .attendee import Attendee
from .filters import f
from .filters import uf
from .environment import Environment
from .options import register_option
from .options import set_option
from .options import get_option
from .build import Build
from .extensions.extension import register_extension
