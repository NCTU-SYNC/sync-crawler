import abc
from collections.abc import Iterable
from typing import Protocol

from google.protobuf import message


class SupportsStr(Protocol):
    def __str__(self) -> str: ...


class BaseWriter(abc.ABC):
    """Base class for writer implementation."""

    @abc.abstractmethod
    def put(
        self,
        _ids: Iterable[SupportsStr],
        messages: Iterable[message.Message],
    ):
        """Store data to storage.

        Args:
            _ids: Object IDs of messages.
            messages: Data to be stored.
        """
        raise NotImplementedError
