"""
The defaults.
"""

import sys

if sys.platform in ('win32', 'cygwin'):
    from teapot.defaults.windows import *
elif sys.platform in ('darwin'):
    from teapot.defaults.osx import *
elif sys.platform.startswith('linux'):
    from teapot.defaults.linux import *
