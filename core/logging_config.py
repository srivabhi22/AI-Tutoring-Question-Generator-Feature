#!/usr/bin/env python3
"""
Central logging configuration.
"""

import logging
import logging.handlers
import os
from typing import Optional


def configure_logging(level: Optional[int] = None) -> None:
    log_level = level if level is not None else logging.INFO
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if not root_logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(logs_dir, "pipeline.log"),
            maxBytes=1_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
