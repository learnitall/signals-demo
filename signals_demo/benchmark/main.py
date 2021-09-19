#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main entrypoint for running a benchmark demo."""
import datetime
import logging

import cowsay

from signals_demo import loginit, util, breakpoint
from signals_demo.benchmark import benchmark


class CowSay(benchmark.Benchmark):
    """How many times can we say cowsay in 5 seconds?"""

    name = "cowsay"

    def get_metric(self):
        count = 0
        start = datetime.datetime.utcnow()
        while (datetime.datetime.utcnow() - start).total_seconds() < 5:
            cowsay.cow("I'm on count {}".format(count))
            count += 1

        return "cowsay_count", count


def run(redis_host: str, redis_port: int, index: str, es_url: str):
    """Run the cowsay benchmark and publish results."""

    cowsay_bench = CowSay(redis_host, redis_port)
    for result in cowsay_bench.run():
        benchmark.publish_result(result, index, es_url)


def main():
    """Parse args from the CLI then run"""

    args = util.get_args()
    logger = logging.getLogger().getChild("benchmark")
    util.wait_for_redis(args.redis_host, args.redis_port, logger)
    util.wait_for_es(args.es_url, logger)
    responder = breakpoint.init_responder(args.redis_host, args.redis_port)

    logger.info("Starting")
    while True:
        breakpoint.breakpoint("benchmark", responder)
        run(args.redis_host, args.redis_port, args.es_index, args.es_url)


if __name__ == "__main__":
    main()
