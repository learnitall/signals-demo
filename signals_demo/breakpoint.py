#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tool for controlling execution flow in the demo."""
import logging

import state_signals

from signals_demo import loginit, util


def init_responder(redis_host: str, redis_port: int) -> state_signals.SignalResponder:
    responder = state_signals.SignalResponder(
        redis_host=redis_host, redis_port=redis_port
    )
    responder.lock_tag("break")
    return responder


def breakpoint(name: str, responder: state_signals.SignalResponder):
    """Wait for continue signal with given name in the metadata."""

    logger = logging.getLogger().getChild("break")
    logger.info("Waiting for continue signal for name '{}'".format(name))

    for signal in responder.listen():
        if (
            signal.event == "continue"
            and signal.metadata is not None
            and signal.metadata["name"] == name
        ):
            responder.srespond(signal, ras=1)
            logger.info("Got continue signal")
            return


def main():
    args = util.get_args()
    logger = logging.getLogger().getChild("breakpoint")
    util.wait_for_redis(args.redis_host, args.redis_port, logger)
    util.wait_for_es(args.es_url, logger)

    logger.info("Creating signal exporter...")
    exporter = state_signals.SignalExporter(
        "break", redis_host=args.redis_host, redis_port=args.redis_port
    )
    exporter.initialize(["continue"], "break")
    pbench_exporter = state_signals.SignalExporter(
        "for pbench", redis_host=args.redis_host, redis_port=args.redis_port
    )
    pbench_exporter.logger.setLevel(logging.ERROR)

    while True:
        user_input = input(
            "Type in name of process to advance (metadata, benchmark, pbench): >>> "
        )
        if user_input.startswith("pbench"):
            pbench_exporter.publish_signal("upload", tag="for pbench")
        else:
            exporter.publish_signal(
                "continue", tag="break", metadata={"name": user_input}
            )


if __name__ == "__main__":
    main()
