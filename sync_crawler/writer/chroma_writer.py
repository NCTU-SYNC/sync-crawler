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
        collection_name: str = 'news',
        embedding_function_name: str = 'distiluse-base-multilingual-cased-v1',
    ):

        self._client = chromadb.HttpClient(host=host, port=port)
        self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_function_name, device=None)
        self._collection = self._client.get_or_create_collection(
            collection_name, embedding_function=self._embedding_function)

    @override
    def put(self, _ids, messages: Iterable[news_pb2.News]):  # pylint: disable=no-member
        _ids = list(map(str, _ids))
        documents = list(map(lambda msg: ' '.join(msg.content), messages))
        embeddings = self._embedding_function(documents)

        self._collection.add(ids=_ids, embeddings=embeddings)
