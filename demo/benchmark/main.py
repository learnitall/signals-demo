#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main entrypoint for running a benchmark demo."""
import argparse
import datetime

import cowsay

from . import benchmark


class CowSay(benchmark.Benchmark):
    """How many times can we say cowsay in 5 seconds?"""

    name = "cowsay"

    def get_metric(self):
        count = 0
        start = datetime.datetime.now()
        while (datetime.datetime.now() - start).total_seconds() < 5:
            cowsay.cow("I'm on count {}".format(count))

        return "cowsay_count", count


def run(redis_host: str, redis_port: int, index: str, es_url: str):
    """Run the cowsay benchmark and publish results."""

    cowsay_bench = CowSay(redis_host, redis_port)
    result = cowsay_bench.run()
    benchmark.publish_result(result, index, es_url)


def main():
    """Parse args from the CLI then run"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--redis-host")
    parser.add_argument("--redis-port")
    parser.add_argument("--es-index")
    parser.add_argument("--es-url")

    args = parser.parse_args()

    run(args.redis_host, args.redis_port, args.es_index, args.es_url)


if __name__ == "__main__":
    main()
