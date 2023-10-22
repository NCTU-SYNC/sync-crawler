from collections.abc import Iterable

import chromadb
from chromadb.utils import embedding_functions
from typing_extensions import override

from proto import news_pb2
from sync_crawler.writer.base_writer import BaseWriter


class ChromaDBWriter(BaseWriter):

    def __init__(
        self,
        host: str = 'localhost',
        port: str = '8000',
        collection: str = 'news',
        embedding_function_name: str = 'distiluse-base-multilingual-cased-v1',
        in_memory: bool = False,
    ):
        """Initialize ChromaDBWriter.

        Args:
            host: Host of ChromaDB server.
            port: Port of ChromaDB server.
            collection: Name of collection.
            embedding_function_name: Name of embedding model. All available
                models can be found [here](https://www.sbert.net/docs/pretrained_models.html)
            in_memory: Whether to use an in-memory database, usually for testing and development.
                If True, `host` and `port` will be ignored.
        """
        if in_memory:
            self._client = chromadb.EphemeralClient()
        else:
            self._client = chromadb.HttpClient(host=host, port=port)
        self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_function_name, device=None)

        self._collection = self._client.get_or_create_collection(
            collection, embedding_function=self._embedding_function)

    @override
    def put(self, _ids, messages: Iterable[news_pb2.News]):  # pylint: disable=no-member
        _ids = list(map(str, _ids))
        documents = list(map(lambda msg: ' '.join(msg.content), messages))
        embeddings = self._embedding_function(documents)

        self._collection.add(ids=_ids, embeddings=embeddings)
