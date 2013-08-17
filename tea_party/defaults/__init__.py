"""
The defaults.
"""

import sys

if sys.platform in ('win32', 'cygwin'):
    from tea_party.defaults.windows import *
elif sys.platform in ('darwin'):
    from tea_party.defaults.osx import *
elif sys.platform.startswith('linux'):
    from tea_party.defaults.linux import *
