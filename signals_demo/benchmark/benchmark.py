#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tools for running benchmarks and getting their results."""
import abc
import dataclasses
import datetime
import logging
import uuid
from typing import Tuple

import state_signals

from signals_demo import breakpoint, export, loginit

_client = None


@dataclasses.dataclass
class BenchmarkResult:
    """Holding basic result information about a benchmark."""

    uuid: str
    name: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    duration: float
    metric_name: str
    metric_value: float


class Benchmark(abc.ABC):
    """Simple abstract class for running a benchmark."""

    name = "Benchmark"

    def __init__(self, redis_host: str, redis_port: int):
        self.uuid = str(uuid.uuid4())
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.logger = logging.getLogger().getChild(self.name)

    @abc.abstractmethod
    def get_metric(self) -> Tuple[str, float]:
        """Run a benchmark and get the resulting metric."""

    def run(self) -> BenchmarkResult:
        """Run the benchmark and return a result."""

        self.logger.info("Preparting to run benchmark '{}'".format(self.name))

        self.logger.info("Creating signal exporter")
        exporter = state_signals.SignalExporter(
            process_name=self.name,
            redis_host=self.redis_host,
            redis_port=self.redis_port,
        )
        exporter.logger = self.logger
        exporter.initialize(legal_events=["start", "end"], tag="demo")

        self.logger.info("Getting metric")

        # Signal that we are starting the benchmark
        exporter.publish_signal(
            "start", tag="demo", timeout=10, metadata={"uuid": self.uuid}
        )

        self.logger.info("Running...")

        start_time = datetime.datetime.utcnow()
        metric_name, metric_value = self.get_metric()
        end_time = datetime.datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        self.logger.info(
            "Got the following metric in {} seconds: '{}={}'".format(
                duration, metric_name, metric_value
            )
        )

        exporter.publish_signal("end", tag="demo", timeout=20)

        return BenchmarkResult(
            uuid=self.uuid,
            name=self.name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            metric_name=metric_name,
            metric_value=metric_value,
        )


def publish_result(result: BenchmarkResult, index: str, es_url: str):
    """Pubilsh the given benchmark result to ES."""

    result_body = dataclasses.asdict(result)
    result_body["timestamp"] = datetime.datetime.utcnow()
    global _client
    _client = export.publish_result(
        result_body, index=index, client=_client, es_url=es_url
    )
