from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import override

from sync_crawler.handlers import DataReader
from sync_crawler.models import News


class BaseCrawler(DataReader, ABC):
    @override
    @abstractmethod
    def read(self, start_from: datetime) -> Iterable[News]:
        """Read data from store.

        Args:
            start_from: Start date to crawl the news.

        Returns:
            Iterable of News.
        """
        pass
