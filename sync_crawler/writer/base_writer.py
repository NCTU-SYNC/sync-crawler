import abc
from collections.abc import Iterable
from typing import Protocol

from google.protobuf import json_format
from google.protobuf import message


class SupportsStr(Protocol):

    def __str__(self) -> str:
        ...


class BaseWriter(abc.ABC):
    """Base class for writer implementation."""

    def _merge_id_and_data(self, _id: SupportsStr, msg: message.Message):
        """Merge object ID and data.

        Args:
            _id: Object ID of messages.
            msg: Data to be stored.

        Returns:
            dict of merged data. {"_id": _id} | data
        """
        id_dict = {"_id": str(_id)}
        data_dict = json_format.MessageToDict(msg)
        return id_dict | data_dict

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
