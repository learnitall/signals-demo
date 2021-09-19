#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tools for exporting benchmark information."""
import logging

from elasticsearch import Elasticsearch

_logger = logging.getLogger().getChild("export")


def publish_result(
    body, index: str, es_url: str = None, client: Elasticsearch = None
) -> Elasticsearch:
    """Publish the given result and return client for further use."""

    if client is None:
        if es_url is None:
            raise TypeError("If client is not given, then es_url needs to be set!")
        _logger.info("Creating a new client instance.")
        client = Elasticsearch([es_url])

    _logger.info("Exporting the following body to index '{}': {}".format(index, body))
    response = client.index(index=index, body=body)
    if response["result"] != "created":
        _logger.warning("Failed to index a result to '{}': {}".format(index, response))
    else:
        _logger.info("Success!")

    return client
