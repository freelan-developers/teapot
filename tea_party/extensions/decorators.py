"""
The extensions decorators.
"""

import re


EXTENSIONS = {}

class NoSuchExtensionError(ValueError):

    """
    No extension exists with the specified name.
    """

    def __init__(self, name):
        """
        Create an NoSuchExtensionError for the specified extension `name`.
        """

        self.name = name

        super(NoSuchExtensionError, self).__init__(
            'No extension with the specified name: %s' % name
            )


class DuplicateExtensionError(ValueError):

    """
    Another extension with the same name exists.
    """

    def __init__(self, name):
        """
        Create a DuplicateExtensionError for the specified extension `name`.
        """

        self.name = name

        super(DuplicateExtensionError, self).__init__(
            'Another extension was already registered with the name %r' % name
            )

class ExtensionParsingError(ValueError):

    """
    No valid extension could be parsed.
    """

    def __init__(self, code):
        """
        Create an ExtensionParsingError for the specified `code`.
        """

        self.code = code

        super(ExtensionParsingError, self).__init__(
            'No extension could be parsed from %r' % code,
        )


class named_extension(object):

    """
    Registers a function to be a extension.
    """

    def __init__(self, name, override=False):
        """
        Registers the function with the specified name.

        If another function was registered with the same name, a
        DuplicateExtensionError will be raised, unless `override` is truthy.
        """

        if name in EXTENSIONS and not override:
            raise DuplicateExtensionError(name)

        self.name = name

    def __call__(self, func):
        """
        Registers the function and returns it unchanged.
        """

        EXTENSIONS[self.name] = func

        return func

def get_extension_by_name(name):
    """
    Get a extension by name.

    If no extension matches the specified name, an NoSuchExtensionError is raised.
    """

    if not name in EXTENSIONS:
        raise NoSuchExtensionError(name=name)

    return EXTENSIONS[name]

def parse_extension(code, builder):
    """
    Parse an extension call in `code` and calls it.

    `builder` will be passed to the extension call as the `builder` argument.
    """

    match = re.match(r'^(?P<name>[a-zA-Z_]+)(\((?P<args>(|(\s*[a-zA-Z_]+\s*)(,\s*\w+\s*)*))\)|)$', code)

    if not match:
        raise ExtensionParsingError(code=code)

    name = match.group('name')
    args = match.group('args')

    if args:
        args = [arg.strip() for arg in args.split(',')]
    else:
        args = []

    extension = get_extension_by_name(name)

    extension(builder, *args)
