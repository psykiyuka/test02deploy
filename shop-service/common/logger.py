import logging
import sys
import os

from .context import request_id_var


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get("-")
        return True


logger = logging.getLogger("shop")


def setup_logger():
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(request_id)s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)

    return logger