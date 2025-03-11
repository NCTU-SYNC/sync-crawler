from collections.abc import Iterable
from typing import override

from llama_index.core import Document, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

from sync_crawler.models.news import News
from sync_crawler.writer.base_writer import BaseWriter


class QdrantConfig(BaseModel):
    host: str = Field(
        "localhost",
        description="Host of QDrant server.",
    )
    port: int = Field(
        6333,
        description="Port of QDrant server.",
    )
    collection: str = Field(
        "news",
        description="Name of collection.",
    )
    embedding_model: str = Field(
        "intfloat/multilingual-e5-large",
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

    excluded_metadata_keys = ["mongo_id", "modified_date"]

    @override
    def write(self, news_items: Iterable[News]):
        docs = [
            Document(
                text=ns.text,
                metadata={
                    "mongo_id": str(ns.mongo_id),
                    "title": ns.title,
                    "category": ns.category,
                    "modified_date": ns.modified_date.timestamp(),
                },
                excluded_embed_metadata_keys=self.excluded_metadata_keys,
                excluded_llm_metadata_keys=self.excluded_metadata_keys,
            )
            for ns in news_items
        ]
        self._index.insert_nodes(docs)
