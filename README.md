# SYNC Crawler

## Description

This is a crawler for the SYNC project. It crawls news articles from different news websites and stores them in a database.

## Installation

This project use [poetry](https://python-poetry.org/) to manage dependencies. Please install it first.

### Execution Only

```bash
# Crawler and mongodb client
poetry install

# Or

# Crawler, mongodb client and qdrant client
# To store data in qdrant, you might need GPUs for execute embedding models
poetry install --with qdrant
```

### Development

```bash
# Crawler and mongodb client
poetry install --with dev
poetry run pre-commit install

# Or

# Crawler, mongodb client and qdrant client
# To store data in qdrant, you might need GPUs for execute embedding models
poetry install --with dev,qdrant
poetry run pre-commit install
```
