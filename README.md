# SYNC Crawler

## Description

This is a crawler for the SYNC project. It crawls news articles from different news websites and stores them in a database.

## Installation

```bash
uv sync --frozen
```

You can also install with the following flags:

* `--no-dev`: Optional. If you don't want to install dev dependencies.
* `--group database`: To install dependencies for storing news in MongoDB and Qdrant. You might need GPUs to execute embedding models.
