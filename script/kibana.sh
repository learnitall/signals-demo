#!/bin/bash
set -xe

curl -X POST "localhost:9200/results/_refresh?pretty"
kubectl port-forward deployment/signals-demo 5601:5601
