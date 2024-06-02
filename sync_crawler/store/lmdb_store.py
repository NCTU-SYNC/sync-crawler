import itertools
import os
import uuid
from collections.abc import Callable

import lmdb
from google.protobuf import message
from typing_extensions import override

from sync_crawler.store.base_store import BaseStore


def _default_key_factory(_m: message.Message) -> bytes:
    return uuid.uuid4().bytes


class LmdbStore(BaseStore):
    def __init__(
        self,
        deserializer: Callable[[bytes], message.Message],
        location=os.path.join("tmp", "news"),
        key_factory: Callable[[message.Message], bytes] = _default_key_factory,
    ) -> None:
        """Initialize LmdbStore.

        Args:
            deserializer: Function to deserialize bytes to message. (Should be a function that
            overrides `google.protobuf.message.Message.FromString`)
            location: Path of the local database.
            key_factory: Function to generate key from message.
        """
        super().__init__(deserializer)

        if not os.path.isdir(location):
            os.makedirs(location, exist_ok=True)
        self._location = location
        self._env = lmdb.open(location)

        self._key_factory = key_factory

    @override
    def put(self, messages):
        key_value_pairs = (
            (self._key_factory(msg), msg.SerializeToString()) for msg in messages
        )

        with (
            self._env.begin(write=True) as txn,
            txn.cursor() as cur,
        ):
            cur.putmulti(key_value_pairs)

    @override
    def pop(self, nums=1):
        values = []

        with self._env.begin(write=True) as txn:
            for key, value in itertools.islice(txn.cursor(), nums):
                values.append(value)
                txn.delete(key)

        return map(self._deserializer, values)

    def __del__(self):
        self._env.close()
