# SYNC Crawler

## Description

This is a crawler for the SYNC project. It crawls news articles from different news websites and stores them in a database.

## Installation

### Execution Only

```bash
# Crawler and mongodb client
uv sync --frozen --no-dev

# Or

# Crawler, mongodb client and qdrant client
# To store data in qdrant, you might need GPUs for execute embedding models
uv sync --frozen --no-dev --group vectordb
```

### Development

```bash
# Crawler and mongodb client
uv sync --frozen
uv run pre-commit install

# Or

# Crawler, mongodb client and vectordb client
# To store data in vectordb, you might need GPUs for executing embedding models
uv sync --frozen --group vectordb
uv run pre-commit install
```
