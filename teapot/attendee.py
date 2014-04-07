"""
An attendee class.
"""

import os
import json

from .memoized import MemoizedObject
from .filters import FilteredObject
from .error import TeapotError
from .source import Source
from .log import LOGGER, Highlight as hl
from .options import get_option
from .path import mkdir, from_user_path


class Attendee(MemoizedObject, FilteredObject):

    """
    Represents a project to build.
    """

    propagate_memoization_key = True

    def __init__(self, name, *args, **kwargs):
        self._depends_on = []
        self._sources = []

        super(Attendee, self).__init__(*args, **kwargs)

    def __repr__(self):
        """
        Get a representation of the attendee.
        """

        return 'Attendee(%r)' % self.name

    def depends_on(self, *attendees):
        """
        Make the attendee depend on one or several other attendees.

        `attendees` is a list of attendees to depend on.
        """

        self._depends_on.extend(attendees)
        return self

    @property
    def cache_path(self):
        return from_user_path(os.path.join(get_option('cache_root'), self.name))

    @property
    def cache_manifest_path(self):
        return os.path.join(self.cache_path, 'manifest.json')

    @property
    def cache_manifest(self):
        try:
            data = json.load(open(self.cache_manifest_path))

            if data:
                return tuple(data)

        except IOError:
            pass

    @cache_manifest.setter
    def cache_manifest(self, value):
        mkdir(self.cache_path)

        json.dump(value, open(self.cache_manifest_path, 'w'))

    @property
    def sources(self):
        """
        Get all the active sources.
        """

        return [x for x in self._sources if x.enabled]

    def add_source(self, resource, *args, **kwargs):
        """
        Add a source to the attendee.

        `resource` is the resource to add to the attendee.
        """

        if not isinstance(resource, Source):
            resource = Source(resource, *args, **kwargs)

        self._sources.append(resource)
        return self

    def fetch(self):
        """
        Fetch the most appropriate source.
        """

        if self.cache_manifest:
            LOGGER.info("%s was already fetched. Nothing to do.", hl(self))
        else:
            LOGGER.debug("Unable to find the download manifest for %s. Will fetch it.", hl(self))
            LOGGER.info('Fetching %s...', hl(self))

            mkdir(self.cache_path)

            if not self.sources:
                raise TeapotError(
                    (
                        "No enabled source was found for the attendee %s. "
                        "Did you forget to set a filter on the attendee ?"
                    ),
                    hl(self),
                )

            for source in self.sources:
                try:
                    self.cache_manifest = source.fetch(target_path=self.cache_path)

                    break
                except TeapotError as ex:
                    LOGGER.debug("Unable to fetch %s: " + ex.msg, hl(source), *ex.args)
                except Exception as ex:
                    LOGGER.debug("Unable to fetch %s: %s", hl(source), hl(str(ex)))

        if not self.cache_manifest:
            raise TeapotError(
                (
                    "All sources failed for the attendee %s. You may want "
                    "to check your network connectivity."
                ),
                hl(self),
            )

        archive_path, archive_type = self.cache_manifest

        LOGGER.debug(
            "Archive for %s (%s) is at: %s",
            hl(self),
            hl(','.join(x for x in archive_type if x)),
            hl(archive_path),
        )
