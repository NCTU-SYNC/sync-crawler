from typing import override

from llama_index.core import Document, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from qdrant_client import QdrantClient

from sync_crawler.models import News
from sync_crawler.writer.base_writer import BaseWriter


class QdrantConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        env_prefix="QDRANT_",
        case_sensitive=True,
        extra="ignore",
    )

    host: str = Field(
        "localhost",
        description="Host of QDrant server.",
        validation_alias="HOST",
    )
    port: int = Field(
        8000,
        description="Port of QDrant server.",
        validation_alias="PORT",
    )
    collection: str = Field(
        "news",
        description="Name of collection.",
        validation_alias="COLLECTION",
    )
    embedding_model: str = Field(
        "sentence-transformers/distiluse-base-multilingual-cased-v1",
        description="Name of embedding model. All available models can be found [here](https://huggingface.co/models?language=zh)",
    )


class QDrantDBWriter(BaseWriter):
    def __init__(
        self,
        config: QdrantConfig,
        in_memory: bool = False,
    ):
        """Initialize QDrantDBWriter.

        Args:
            config: Configuration for QDrant database.
            in_memory: Whether to use an in-memory database, usually for testing and development.
        """
        if in_memory:
            self._client = QdrantClient(":memory:")
        else:
            self._client = QdrantClient(
                host=config.host,
                port=config.port,
            )

        self._index = VectorStoreIndex.from_vector_store(
            vector_store=QdrantVectorStore(
                client=self._client, collection_name=config.collection
            ),
            embed_model=HuggingFaceEmbedding(model_name=config.embedding_model),
        )

    @staticmethod
    def _get_metadata(news: News):
        return news.model_dump(include={"title", "category"}) | {
            "modified_date": news.modified_date.timestamp()
        }

    excluded_metadata_keys = ["modified_date"]

    @override
    def write(self, news_with_id):
        docs = [
            Document(
                doc_id=str(id_),
                text=ns.text,
                extra_info=self._get_metadata(ns),
                excluded_embed_metadata_keys=self.excluded_metadata_keys,
                excluded_llm_metadata_keys=self.excluded_metadata_keys,
            )
            for id_, ns in news_with_id
        ]
        self._index.insert_nodes(docs)
