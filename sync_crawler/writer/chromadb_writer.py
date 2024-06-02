from collections.abc import Iterable

import chromadb
from llama_index.core import Document, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from typing_extensions import override

from sync_crawler.protos import news_pb2
from sync_crawler.writer.base_writer import BaseWriter


class ChromaDBWriter(BaseWriter):
    def __init__(
        self,
        host: str = "localhost",
        port: str = "8000",
        collection: str = "news",
        embedding_function_name: str = "sentence-transformers/distiluse-base-multilingual-cased-v1",
        in_memory: bool = False,
    ):
        """Initialize ChromaDBWriter.

        Args:
            host: Host of ChromaDB server.
            port: Port of ChromaDB server.
            collection: Name of collection.
            embedding_function_name: Name of embedding model. All available
                models can be found [here](https://huggingface.co/models?language=zh)
            in_memory: Whether to use an in-memory database, usually for testing and development.
                If True, `host` and `port` will be ignored.
        """
        if in_memory:
            self._client = chromadb.EphemeralClient()
        else:
            self._client = chromadb.HttpClient(host=host, port=port)

        self._collection = self._client.get_or_create_collection(collection)

        self._index = VectorStoreIndex.from_vector_store(
            vector_store=ChromaVectorStore(chroma_collection=self._collection),
            embed_model=HuggingFaceEmbedding(model_name=embedding_function_name),
        )

    @override
    def put(self, _ids, messages: Iterable[news_pb2.News]):  # pylint: disable=no-member
        docs = [
            Document(doc_id=str(_id), text=" ".join(msg.content))
            for _id, msg in zip(_ids, messages)
        ]
        self._index.insert_nodes(docs)
