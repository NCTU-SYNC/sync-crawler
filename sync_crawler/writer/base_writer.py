import abc
from collections.abc import Iterable
from typing import Protocol

from sync_crawler.models import News


class SupportsStr(Protocol):
    def __str__(self) -> str: ...


class BaseWriter(abc.ABC):
    """Base class for writer implementation."""

    @abc.abstractmethod
    def put(
        self,
        ids: Iterable[SupportsStr],
        news: Iterable[News],
    ):
        """Store data to storage.

        Args:
            ids: Object IDs of each news.
            news: News to be stored.
        """
        raise NotImplementedError
