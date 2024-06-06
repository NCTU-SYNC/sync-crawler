import abc
from collections.abc import Iterable

from sync_crawler.models import News


class BaseStore(abc.ABC):
    """Base class for store implementation."""

    @abc.abstractmethod
    def put(self, news: Iterable[News]):
        """Store data to storage.

        Args:
            news: News to be stored.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def pop(self, nums=1) -> Iterable[News]:
        """Fetch data from store then delete them.

        Args:
            nums: Number of data to be popped. If the remaining data is less than `nums`, all
                remaining data will be popped.

        Returns:
            List of popped data.
        """
        raise NotImplementedError
