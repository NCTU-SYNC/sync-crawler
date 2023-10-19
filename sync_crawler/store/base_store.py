import abc
from collections.abc import Callable
from collections.abc import Iterable

from google.protobuf import message


class BaseStore(abc.ABC):
    """Base class for store implementation.

    Usage:
        ```python
        from google.protobuf import json_format

        from proto import news_pb2
        from sync_crawler.store import LmdbStore

        data = news_pb2.News()

        store = LmdbStore(deserializer=news_pb2.News.FromString)
        store.put([data])

        outputs = list(store.pop())
        print(json_format.MessageToJson(outputs[0]))
        ```
    """

    def __init__(
        self,
        deserializer: Callable[[bytes], message.Message],
    ):
        """Initialize BaseStore.

        Args:
            deserializer: Function to deserialize bytes to message. (Should be a function that
            overrides `google.protobuf.message.Message.FromString`)
        """
        self._deserializer = deserializer

    @abc.abstractmethod
    def put(self, messages: Iterable[message.Message]):
        """Store data to storage.

        Args:
            messages: Data to be stored.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def pop(self, nums=1) -> Iterable[message.Message]:
        """Fetch data from store then delete them.

        Args:
            nums: Number of data to be popped. If the remaining data is less than `nums`, all
                remaining data will be popped.

        Returns:
            List of popped data.
        """
        raise NotImplementedError
