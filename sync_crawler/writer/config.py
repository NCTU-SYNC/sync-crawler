from pydantic_settings import BaseSettings, SettingsConfigDict

from sync_crawler.writer.mongodb_writer import MongoConfig
from sync_crawler.writer.qdrant_writer import QdrantConfig


class WriterConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
    )
    mongo: MongoConfig
    qdrant: QdrantConfig
