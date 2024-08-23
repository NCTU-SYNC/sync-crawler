import hashlib
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import override

from sync_crawler.handlers import DataReader
from sync_crawler.models import News


def ignore_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return None

    return wrapper


class BaseCrawler(DataReader, ABC):
    media_name: str

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

    def hash(self, data: str) -> str:
        return hashlib.sha1(data.encode("utf-8")).hexdigest()

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(self.media_name)
