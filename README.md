# SYNC Crawler

## Description

This is a crawler for the SYNC project. It crawls news articles from different news websites and stores them in a database.

## Installation

This project use [poetry](https://python-poetry.org/) to manage dependencies. Please install it first.

### Execution Only

```bash
poetry install --without dev
```

### Development

```bash
poetry install
poetry run pre-commit install
```

## Protocol Buffer Code Generation

> You can just use the pre-generated code in this repository or regenerate it by yourself.

Please follow the instructions of the [protobuf](https://github.com/protocolbuffers/protobuf) repository to install the compiler `protoc`.

```bash
protoc --python_out=pyi_out:. proto/news.proto
```
