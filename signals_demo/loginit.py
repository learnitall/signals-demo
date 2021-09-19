#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""When imported, will setup root logger with stream handler."""
import logging
import sys

HAVE_BEEN_SETUP = False


def setup():
    """Initialize logging."""

    global HAVE_BEEN_SETUP
    if HAVE_BEEN_SETUP:
        return

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(stream_handler)

    HAVE_BEEN_SETUP = True


setup()
