"""
tea-party 'attendee' class.
"""

import os
import json
import errno

from tea_party.log import LOGGER
from tea_party.source import make_sources


def make_attendees(data):
    """
    Build a list of attendees from an attendees data dictionary.
    """

    return [
        make_attendee(name, attributes)
        for name, attributes
        in data.items()
    ]


def make_attendee(name, attributes):
    """
    Create an attendee from a name a dictionary of attributes.
    """

    return Attendee(
        name=name,
        sources=make_sources(attributes.get('source')),
        depends=make_depends(attributes.get('depends')),
    )


def make_depends(depends):
    """
    Create a list of dependencies.

    `depends` can either be a single dependency name or a list of dependencies.

    If `depends` is False, an empty list is returned.
    """

    if not depends:
        return []

    elif isinstance(depends, basestring):
        return [depends]

    return depends


class Attendee(object):

    """
    An `Attendee` instance holds information about an attendee (third-party
    software).
    """

    ARCHIVE_INFO_FILENAME = 'archive_info.json'

    def __init__(self, name, sources, depends):
        """
        Create an attendee.

        `sources` is a list of Source instances.
        `depends` is a list of Attendee names to depend on.
        """

        if not sources:
            raise ValueError('A list one source must be specified for %s' % name)

        self.name = name
        self.sources = sources
        self.depends = depends

    def __unicode__(self):
        """
        Get a unicode representation of the attendee.
        """

        return self.name

    def __str__(self):
        """
        Get the name of the attendee.
        """

        return self.name

    def __repr__(self):
        """
        Get a representation of the source.
        """

        return '<%s.%s(name=%r, sources=%r, depends=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.name,
            self.sources,
            self.depends,
        )

    def fetch(self, root_path, context):
        """
        Fetch the specified attendee archives at the specified `root_path`.

        If the fetching suceeds, the succeeding source is returned.
        If the fetching fails, a RuntimeError is raised.
        """

        for source in self.sources:
            archive_info = source.fetch(root_path=root_path, context=context)
            archive_info['archive_path'] = os.path.relpath(archive_info['archive_path'], root_path)

            with open(os.path.join(root_path, self.ARCHIVE_INFO_FILENAME), 'w') as archive_info_file:
                return json.dump(archive_info, archive_info_file)

            return source

        raise RuntimeError('All sources failed for %s' % self.name)

    def get_archive_info(self, root_path):
        """
        Get the associated archive info.

        Returns a dict containing the archive information.

        If the archive information or the archive does not exist, nothing is
        returned.
        """

        try:
            with open(os.path.join(root_path, self.ARCHIVE_INFO_FILENAME)) as archive_info_file:
                return json.load(archive_info_file)

        except IOError as ex:
            if ex.errno != errno.ENOENT:
                raise
        except ValueError:
            pass

    def needs_fetching(self, root_path):
        """
        Check if the attendee needs fetching.
        """

        archive_info = self.get_archive_info(root_path)

        if archive_info:
            if os.path.isfile(os.path.join(root_path, archive_info.get('archive_path'))):
                LOGGER.debug('%s does not need fetching.', self)
                return False

        LOGGER.debug('%s needs fetching.', self)

        return True
