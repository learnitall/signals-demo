#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Responds to signals by collecting metadata about a run."""
import argparse
import datetime
import logging
import platform
from typing import Any, Dict

import kubernetes.client
import kubernetes.config
import state_signals

from .. import export


def get_metadata(kube_client) -> Dict[str, Any]:
    """Return basic dict with metadata about the host."""

    metadata = {
        "python": platform.python_implementation(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "kernel": platform.release(),
    }
    # assume we only have one node, since we are just on minikube
    node_info = kube_client.list_node()["items"][0]["status"]["node_info"]
    metadata.update(node_info)

    return metadata


def run(redis_host: str, redis_port: int, index: str, es_url: str):
    """Collect metadata when responding to a signal."""

    logger = logging.getLogger().getChild("metadata")
    es_client = None

    logger.info("Creating signal responder")
    responder = state_signals.SignalResponder(
        redis_host, redis_port, responder_name="metadata"
    )
    responder.logger = logger
    responder.lock_tag("demo")

    logger.info("Creating kubernetes client")
    kubernetes.config.load_kube_config()
    kube_client = kubernetes.client.CoreV1Api()

    for signal in responder.listen():
        logger.info(
            "Got '{}' event from '{}'".format(signal.event, signal.process_name)
        )

        if signal.event == "start":
            if signal.metadata is None:
                logger.warning("Expected uuid in metadata, instead got None. Ignoring")
                continue
            logger.info("Reacting to uuid '{}'".format(signal.metadata["uuid"]))

            logger.info("Getting metadata...")
            metadata = get_metadata(kube_client)
            metadata["timestamp"] = datetime.datetime.now()
            metadata["uuid"] = signal.metadata["uuid"]

            logger.info("Publishing metadata...")
            _es_client = export.publish_result(
                metadata, index=index, es_url=es_url, client=_es_client
            )

            logger.info("Sending success response...")
            responder.srespond(signal=signal, ras=0)

            logger.info("Done!")


def main():
    """Parse args from the CLI then run"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--redis-host")
    parser.add_argument("--redis-port")
    parser.add_argument("--es-index")
    parser.add_argument("--es-url")

    args = parser.parse_args()

    run(args.redis_host, args.redis_port, args.es_index, args.es_url)
