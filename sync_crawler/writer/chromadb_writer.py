from typing import override

import chromadb
from chromadb.config import Settings
from llama_index.core import Document, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from sync_crawler.models import News
from sync_crawler.writer.base_writer import BaseWriter


class ChromaDBWriter(BaseWriter):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        token: str = "",
        collection: str = "news",
        embedding_model: str = "sentence-transformers/distiluse-base-multilingual-cased-v1",
        in_memory: bool = False,
    ):
        """Initialize ChromaDBWriter.

        Args:
            host: Host of ChromaDB server.
            port: Port of ChromaDB server.
            token: Token for authentication.
            collection: Name of collection.
            embedding_model: Name of embedding model. All available
                models can be found [here](https://huggingface.co/models?language=zh)
            in_memory: Whether to use an in-memory database, usually for testing and development.
                If True, `host` and `port` will be ignored.
        """
        if in_memory:
            self._client = chromadb.EphemeralClient()
        else:
            self._client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(
                    chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                    chroma_client_auth_credentials=token,
                ),
            )

        self._collection = self._client.get_or_create_collection(collection)

        self._index = VectorStoreIndex.from_vector_store(
            vector_store=ChromaVectorStore(chroma_collection=self._collection),
            embed_model=HuggingFaceEmbedding(model_name=embedding_model),
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
