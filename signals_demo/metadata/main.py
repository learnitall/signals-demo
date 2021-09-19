#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Responds to signals by collecting metadata about a run."""
import datetime
import logging
import platform
from typing import Any, Dict
import pprint

import kubernetes.client
import kubernetes.config
import state_signals

from signals_demo import breakpoint, export, loginit, util


def get_metadata(kube_client) -> Dict[str, Any]:
    """Return basic dict with metadata about the host."""

    metadata = {
        "python": platform.python_implementation(),
        "python_version": platform.python_version(),
        "hostname_vm_host": platform.node(),
        "kernel_vm_host": platform.release(),
    }
    # assume we only have one node, since we are just on minikube
    node_info = kube_client.list_node().items[0].status.node_info.to_dict()
    metadata.update(node_info)

    return metadata


def run(redis_host: str, redis_port: int, index: str, es_url: str):
    """Collect metadata when responding to a signal."""

    logger = logging.getLogger().getChild("metadata")

    util.wait_for_redis(redis_host, redis_port, logger)
    responder = breakpoint.init_responder(redis_host, redis_port)
    es_client = None
    util.wait_for_es(es_url, logger)

    logger.info("Waiting for continue...")
    breakpoint.breakpoint("metadata", responder)

    logger.info("Creating signal responder")
    responder = state_signals.SignalResponder(
        redis_host, redis_port, responder_name="metadata"
    )
    responder.logger = logger
    responder.lock_tag("for pbench")

    logger.info("Creating kubernetes client")
    kubernetes.config.load_kube_config()
    kube_client = kubernetes.client.CoreV1Api()

    logger.info("Waiting for events...")

    for signal in responder.listen():
        logger.info(
            "Got '{}' event from '{}'".format(signal.event, signal.process_name)
        )

        if signal.event == "benchmark_start":
            if signal.metadata is None:
                logger.warning("Expected uuid in metadata, instead got None. Ignoring")
                continue
            logger.info("Reacting to uuid '{}'".format(signal.metadata["uuid"]))

            logger.info("Getting metadata...")
            metadata = get_metadata(kube_client)
            metadata["timestamp"] = datetime.datetime.utcnow()
            metadata["uuid"] = signal.metadata["uuid"]
            logger.info("Got the following metadata: {}".format(pprint.pformat(metadata)))

            logger.info("Publishing metadata...")
            es_client = export.publish_result(
                metadata, index=index, es_url=es_url, client=es_client
            )

            logger.info("Sending success response...")
            responder.srespond(signal=signal, ras=0)

            logger.info("Done!")
            logger.info("Waiting for more events...")


def main():
    """Parse args from the CLI then run"""

    args = util.get_args()
    run(args.redis_host, args.redis_port, args.es_index, args.es_url)


if __name__ == "__main__":
    main()
