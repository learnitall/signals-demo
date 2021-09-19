#!/bin/bash
set -xe

pip install poetry
poetry install

poetry run python -m signals_demo.breakpoint \
    --redis-host localhost \
    --redis-port 6379 \
    --es-url http://localhost:9200