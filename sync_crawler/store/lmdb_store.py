import itertools
import os
import pickle
import uuid
from collections.abc import Callable, Iterable
from typing import override

import lmdb

from sync_crawler.models import News
from sync_crawler.store.base_store import BaseStore


def _default_key_factory(_m: News) -> bytes:
    return uuid.uuid4().bytes


class LmdbStore(BaseStore):
    def __init__(
        self,
        location=os.path.join("tmp", "news"),
        key_factory: Callable[[News], bytes] = _default_key_factory,
    ) -> None:
        """Initialize LmdbStore.

        Args:
            location: Path of the local database.
            key_factory: Function to generate key from message.
        """
        if not os.path.isdir(location):
            os.makedirs(location, exist_ok=True)
        self._location = location
        self._env = lmdb.open(location)

        self._key_factory = key_factory

    @override
    def put(self, news: Iterable[News]):
        key_value_pairs = ((self._key_factory(ns), pickle.dumps(ns)) for ns in news)

        with (
            self._env.begin(write=True) as txn,
            txn.cursor() as cur,
        ):
            cur.putmulti(key_value_pairs)

    @override
    def pop(self, nums=1) -> Iterable[News]:
        values: Iterable[News] = []

        with self._env.begin(write=True) as txn:
            for key, value in itertools.islice(txn.cursor(), nums):
                values.append(pickle.loads(value))
                txn.delete(key)

        return values

    def __del__(self):
        self._env.close()
