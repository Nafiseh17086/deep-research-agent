"""Structured logging using Rich for pretty console output."""

import logging
from rich.console import Console
from rich.logging import RichHandler

console = Console()


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a Rich-formatted logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            show_path=False,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger
