# SYNC Crawler

## Description

This is a crawler for the SYNC project. It crawls news articles from different news websites and stores them in a database.

## Installation

```bash
uv sync --frozen
```

You can also install with the following flags:

* `--no-dev`: Optional. If you don't want to install dev dependencies.
* `--extra crawler`: To install dependencies for crawling news articles.
* `--extra database`: To install dependencies for storing news in MongoDB and Qdrant. You might need GPUs to execute embedding models.
* `--extra migration`: To install dependencies for migrating data from MongoDB to Qdrant. You might need GPUs to execute embedding models.

## Environment Variables

The following environment variables are **only needed if you want to store crawled data in the database**. The core crawler functionality doesn't require these variables. They should be defined in a `.env` file:

| Variable          | Description                                          |
| ----------------- | ---------------------------------------------------- |
| MONGO_URL         | MongoDB connection string                            |
| MONGO_DATABASE    | MongoDB database name                                |
| MONGO_COLLECTION  | MongoDB collection name for storing news articles    |
| QDRANT_HOST       | Hostname or IP address of the Qdrant vector database |
| QDRANT_PORT       | Port number for the Qdrant server                    |
| QDRANT_COLLECTION | Qdrant collection name for storing news embeddings   |

## Configuration

The following configuration is **only needed for database operations**. The core crawler can function without this configuration.

The crawler uses a TOML configuration file located at `configs/config.toml` with the following options:
