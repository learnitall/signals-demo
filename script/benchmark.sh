#!/bin/bash
set -xe

pip install poetry
poetry install

poetry run python -m signals_demo.benchmark.main \
    --redis-host localhost \
    --redis-port 6379 \
    --es-index results \
    --es-url http://localhost:9200
