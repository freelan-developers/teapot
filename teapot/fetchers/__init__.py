"""
Contains all teapot fetchers logic.
"""

from teapot.fetchers.fetcher import Fetcher
from teapot.fetchers.fetcher import register_fetcher
from teapot.fetchers.file_fetcher import FileFetcher  # NOQA
from teapot.fetchers.http_fetcher import HttpFetcher  # NOQA
from teapot.fetchers.github_fetcher import GithubFetcher  # NOQA
