import argparse
import logging
import os
import tomllib

from llama_index.core import Document
from llama_index.readers.mongodb import SimpleMongoReader
from tqdm.auto import tqdm

from sync_crawler.writer import QDrantDBWriter, WriterConfig


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

    mongo_reader = SimpleMongoReader(uri=config.mongo.url)

    n_docs = mongo_reader.client[config.mongo.database][
        config.mongo.collection
    ].count_documents({})
    print(f"Total documents to migrate: {n_docs}")

    qdrant_writer = QDrantDBWriter(config.qdrant)

    docs = mongo_reader.lazy_load_data(
        db_name=config.mongo.database,
        collection_name=config.mongo.collection,
        field_names=["content"],
        metadata_names=[
            "_id",
            "title",
            "category",
            "modified_date",
        ],
    )

    for doc in tqdm(docs, total=n_docs, dynamic_ncols=True):
        qdrant_doc = Document(
            id_=str(doc.metadata["_id"]),
            text_resource=doc.text,
            metadata={
                "title": doc.metadata["title"],
                "category": doc.metadata["category"],
                "modified_date": doc.metadata["modified_date"].timestamp(),
            },
            excluded_embed_metadata_keys=QDrantDBWriter.excluded_metadata_keys,
            excluded_llm_metadata_keys=QDrantDBWriter.excluded_metadata_keys,
        )

        qdrant_writer._index.insert_nodes([qdrant_doc])
