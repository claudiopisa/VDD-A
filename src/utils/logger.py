import logging
import os


DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s"


def setup_logging(level: str | int | None = None, fmt: str = DEFAULT_FORMAT) -> None:
    if level is None:
        level = os.getenv("VDD_LOG_LEVEL", "INFO")

    if isinstance(level, str):
        normalized_level = getattr(logging, level.upper(), logging.INFO)
    else:
        normalized_level = level

    root_logger = logging.getLogger()
    root_logger.setLevel(normalized_level)

    if not root_logger.handlers:
        logging.basicConfig(level=normalized_level, format=fmt)
    else:
        for handler in root_logger.handlers:
            handler.setLevel(normalized_level)
            handler.setFormatter(logging.Formatter(fmt))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
