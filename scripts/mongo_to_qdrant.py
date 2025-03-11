import argparse
import logging
import os
import tomllib
from collections.abc import Callable, Iterable

from llama_index.core import Document
from llama_index.readers.mongodb import SimpleMongoReader
from tqdm.auto import tqdm

from sync_crawler.writer import QDrantDBWriter, WriterConfig


class MongoReader(SimpleMongoReader):
    """Add a custom `field_extractors`.

    Check the [pull request](https://github.com/run-llama/llama_index/pull/18063) for more details.

    """

    def lazy_load_data(
        self,
        db_name: str,
        collection_name: str,
        field_names: list[str] = ["text"],
        separator: str = "",
        query_dict: dict | None = None,
        max_docs: int = 0,
        metadata_names: list[str] | None = None,
        field_extractors: dict[str, Callable[..., str]] | None = None,
    ) -> Iterable[Document]:
        """Load data from the input directory.

        Args:
            db_name (str): name of the database.
            collection_name (str): name of the collection.
            field_names(List[str]): names of the fields to be concatenated.
                Defaults to ["text"]
            separator (str): separator to be used between fields.
                Defaults to ""
            query_dict (Optional[Dict]): query to filter documents. Read more
            at [official docs](https://www.mongodb.com/docs/manual/reference/method/db.collection.find/#std-label-method-find-query)
                Defaults to None
            max_docs (int): maximum number of documents to load.
                Defaults to 0 (no limit)
            metadata_names (Optional[List[str]]): names of the fields to be added
                to the metadata attribute of the Document. Defaults to None
            field_extractors (Optional[Dict[str, Callable[..., str]]]): dictionary
                containing field name and a function to extract text from the field.
                The default extractor function is `str`. Defaults to None.

        Returns:
            Iterable[Document]: A list of documents.
        """
        db = self.client[db_name]
        cursor = db[collection_name].find(
            filter=query_dict or {},
            limit=max_docs,
            projection={name: 1 for name in field_names + (metadata_names or [])},
        )

        field_extractors = field_extractors or {}

        for item in cursor:
            try:
                texts = [
                    field_extractors.get(name, str)(item[name]) for name in field_names
                ]
            except KeyError as err:
                raise ValueError(
                    f"{err.args[0]} field not found in Mongo document."
                ) from err

            text = separator.join(texts)

            if metadata_names is None:
                yield Document(text=text, id_=str(item["_id"]))
            else:
                try:
                    metadata = {name: item.get(name) for name in metadata_names}
                    metadata["collection"] = collection_name
                except KeyError as err:
                    raise ValueError(
                        f"{err.args[0]} field not found in Mongo document."
                    ) from err
                yield Document(text=text, id_=str(item["_id"]), metadata=metadata)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join("configs", "config.toml"),
        help="Path to the config file.",
    )
    return parser.parse_args()


def load_config(config_path: str):
    try:
        with open(config_path, "rb") as config_file:
            config = tomllib.load(config_file)
    except FileNotFoundError:
        msg = f"Config file not found at: {config_path}"
        logging.error(msg)
        exit(1)
    except Exception as e:
        msg = f"Error loading config file: {config_path} - {e}"
        logging.error(msg)
        exit(1)

    return WriterConfig.model_validate(config)


if __name__ == "__main__":
    args = parse_args()
    config = load_config(args.config)

    mongo_reader = MongoReader(uri=config.mongo.url)

    n_docs = mongo_reader.client[config.mongo.database][
        config.mongo.collection
    ].count_documents({})
    print(f"Total documents to migrate: {n_docs}")

    qdrant_writer = QDrantDBWriter(config.qdrant)

    docs = mongo_reader.lazy_load_data(
        db_name=config.mongo.database,
        collection_name=config.mongo.collection,
        field_names=["content"],
        field_extractors={
            "content": lambda x: "".join(x),
        },
        metadata_names=[
            "_id",
            "title",
            "category",
            "modified_date",
        ],
    )

    for doc in tqdm(docs, total=n_docs, dynamic_ncols=True):
        qdrant_doc = Document(
            text=doc.text,
            metadata={
                "mongo_id": str(doc.metadata["_id"]),
                "title": doc.metadata["title"],
                "category": doc.metadata["category"],
                "modified_date": doc.metadata["modified_date"].timestamp(),
            },
            excluded_embed_metadata_keys=QDrantDBWriter.excluded_metadata_keys,
            excluded_llm_metadata_keys=QDrantDBWriter.excluded_metadata_keys,
        )

        qdrant_writer._index.insert_nodes([qdrant_doc])
