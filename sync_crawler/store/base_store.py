from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import override

from sync_crawler.handlers import DataReader, DataWriter
from sync_crawler.models import News


class BaseStore(DataReader, DataWriter, ABC):
    @override
    @abstractmethod
    def read(self, num: int | None = None) -> Iterable[News]:
        """Read data from store.

        Args:
            num: Number of data to read. Defaults to None, read all data.

        Returns:
            Iterable of News.
        """
        pass

    @override
    @abstractmethod
    def write(self, news_items: Iterable[News]):
        """Write data to store.

        Args:
            news_items: Iterable of News to be written.
        """
        pass
