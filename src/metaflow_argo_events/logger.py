from __future__ import annotations

import os
import sys

import loguru
from loguru import logger

DEFAULT_LOG_LEVEL = os.environ.get("METAFLOW_EVENTS_LOG_LEVEL", "INFO").upper()

BASE_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

VERBOSE_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.remove()
logger.add(sys.stderr, level=DEFAULT_LOG_LEVEL, format=BASE_LOG_FORMAT)


def get_logger(name: str) -> loguru.Logger:
    """Get a logger instance bound to a specific name."""
    return logger.bind(name=name)


def configure_verbose_logging(*, verbose: bool = False) -> None:
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", format=VERBOSE_LOG_FORMAT)
        logger.debug("Verbose logging enabled")


def get_log_level() -> str:
    """Get the current log level."""
    return os.environ.get("METAFLOW_EVENTS_LOG_LEVEL", DEFAULT_LOG_LEVEL)


def set_log_level(level: str) -> None:
    level = level.upper()
    os.environ["METAFLOW_EVENTS_LOG_LEVEL"] = level
    logger.remove()
    logger.add(sys.stderr, level=level, format=BASE_LOG_FORMAT)
    logger.info(f"Log level set to {level}")


def get_context_logger(
    ctx_name: str | None = None,
    **context_kwargs: str | float | bool | None,
) -> loguru.Logger:
    context: dict[str, str | float | bool | None] = {}
    if ctx_name:
        context["ctx"] = ctx_name
    context.update(context_kwargs)
    return logger.bind(**context)
