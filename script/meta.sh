#!/bin/bash
set -xe

ps aux | grep -i 'kubectl port-forward' | awk '{print $2}' | xargs kill || true
kubectl port-forward deployment/signals-demo 9200:9200 &
kubectl port-forward deployment/signals-demo 6379:6379 &

poetry run python -m signals_demo.metadata.main \
    --redis-host localhost \
    --redis-port 6379 \
    --es-index results \
    --es-url http://localhost:9200
