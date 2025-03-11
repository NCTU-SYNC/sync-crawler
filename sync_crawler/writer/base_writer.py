from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import override

from sync_crawler.handlers import DataWriter
from sync_crawler.models import News


class BaseWriter(DataWriter, ABC):
    @override
    @abstractmethod
    def write(
        self,
        news_items: Iterable[News],
    ):
        pass
