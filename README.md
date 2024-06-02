# SYNC Crawler

## Description

This is a crawler for the SYNC project. It crawls news articles from different news websites and stores them in a database.

## Installation

This project use [poetry](https://python-poetry.org/) to manage dependencies. Please install it first.

### Execution Only

```bash
poetry install --without dev
poetry run gen-protos
```

### Development

```bash
poetry install
poetry run gen-protos
poetry run pre-commit install
```

## Protocol Buffer Code Generation

```bash
poetry run gen-protos
```
