from typing import override

import pymongo
from bson import ObjectId
from pydantic import BaseModel, Field

from sync_crawler.writer.base_writer import BaseWriter


class MongoConfig(BaseModel):
    url: str = Field(
        "mongodb://localhost:8000",
        description="A [MongoDB url](https://www.mongodb.com/docs/manual/reference/connection-string/) to connect to.",
    )
    database: str = Field(
        "SYNC",
        description="Name of database.",
    )
    collection: str = Field(
        "News",
        description="Name of collection.",
    )


class MongoDBWriter(BaseWriter):
    def __init__(
        self,
        config: MongoConfig,
        in_memory: bool = False,
    ) -> None:
        """Initialize MongoDBWriter.

        Args:
            config: Configuration for MongoDB database.
            in_memory: Whether to use an in-memory database, usually for testing and development..
        """
        if in_memory:
            import pymongo_inmemory

            self._client = pymongo_inmemory.MongoClient()
        else:
            self._client = pymongo.MongoClient(config.url)
        self._collection = self._client[config.database][config.collection]

    @override
    def write(self, news_with_id):
        news_dicts = (
            {"_id": ObjectId(str(_id)), **ns.model_dump()} for _id, ns in news_with_id
        )
        self._collection.insert_many(news_dicts)
