from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Optional, override

from sync_crawler.handlers import DataReader, DataWriter
from sync_crawler.models import News


class BaseStore(DataReader, DataWriter, ABC):
    @override
    @abstractmethod
    def read(self, num: Optional[int] = None) -> Iterable[News]:
        """Read data from store.

        Args:
            num: Number of data to read. Defaults to None, read all data.

        Returns:
            Iterable of News.
        """
        pass

    @override
    @abstractmethod
    def write(self, news: Iterable[News]):
        """Write data to store.

        Args:
            news: Iterable of News to be written.
        """
        pass
