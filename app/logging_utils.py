import json
import logging
from datetime import datetime

logger = logging.getLogger("app")


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=level,
        format="%(message)s",  # raw JSON only
    )


def log_event(data: dict):
    logger.info(json.dumps(data))
