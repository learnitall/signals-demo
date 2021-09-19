#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common utility functions"""
import argparse
import time

import elasticsearch
import redis


def wait_for_redis(redis_host, redis_port, logger):
    """Wait for redis to come up by polling."""

    logger.info("Waiting for redis...")
    r = redis.Redis(host=redis_host, port=redis_port)
    while True:
        try:
            r.ping()
            break
        except redis.exceptions.ConnectionError:
            # Lazy polling since it won't take long to come up
            time.sleep(0.5)


def wait_for_es(es_url: str, logger):
    """Wait for es to come up by polling."""

    logger.info("Waiting for es...")
    es = elasticsearch.Elasticsearch(hosts=[es_url])
    while not es.ping():
        time.sleep(0.5)


def get_args() -> argparse.Namespace:
    """Get common arguments for redis and es connections."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--redis-host")
    parser.add_argument("--redis-port")
    parser.add_argument("--es-url")
    parser.add_argument("--es-index")

    args = parser.parse_args()

    return args
