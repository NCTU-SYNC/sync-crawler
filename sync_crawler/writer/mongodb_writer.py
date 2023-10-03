import pymongo
from typing_extensions import override

from sync_crawler.writer.base_writer import BaseWriter


class MongoDBWriter(BaseWriter):

    def __init__(self, url: str, database: str, collection: str) -> None:
        """Initialize MongoDBWriter.

        Args:
            url: A [MongoDB url](https://www.mongodb.com/docs/manual/reference/connection-string/)
            to connect to.
            database: Name of database.
            collection: Name of collection.
        """
        self._client = pymongo.MongoClient(url)
        self._collection = self._client[database][collection]

    @override
    def put(self, _ids, messages):
        message_dicts = map(self._merge_id_and_data, _ids, messages)

        result = self._collection.insert_many(message_dicts)

        return result
