import pymongo
from google.protobuf import json_format
from typing_extensions import override

from sync_crawler.writer.base_writer import BaseWriter


class MongoDBWriter(BaseWriter):
    def __init__(
        self,
        url: str = "mongodb://localhost:8000",
        database: str = "SYNC",
        collection: str = "News",
        in_memory: bool = False,
    ) -> None:
        """Initialize MongoDBWriter.

        Args:
            url: A [MongoDB url](https://www.mongodb.com/docs/manual/reference/connection-string/)
            to connect to.
            database: Name of database.
            collection: Name of collection.
            in_memory: Whether to use an in-memory database, usually for testing and development.
                If True, `url` will be ignored.
        """
        if in_memory:
            import pymongo_inmemory  # pylint: disable=import-outside-toplevel

            self._client = pymongo_inmemory.MongoClient()
        else:
            self._client = pymongo.MongoClient(url)
        self._collection = self._client[database][collection]

    @override
    def put(self, _ids, messages):
        message_dicts = (
            {"_id": str(_id), **json_format.MessageToDict(msg)}
            for _id, msg in zip(_ids, messages)
        )

        self._collection.insert_many(message_dicts)
