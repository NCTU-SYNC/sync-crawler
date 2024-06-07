from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Protocol, override

from sync_crawler.handlers import DataWriter
from sync_crawler.models import News


class SupportsStr(Protocol):
    def __str__(self) -> str: ...


class BaseWriter(DataWriter, ABC):
    @override
    @abstractmethod
    def write(
        self,
        news_with_id: Iterable[tuple[SupportsStr, News]],
    ):
        """Store data to storage.

        Args:
            news_with_id: Iterable of tuple of id and News.
        """
        pass
