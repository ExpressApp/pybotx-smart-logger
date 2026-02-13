"""Schemas for smart logger internals."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class LogEntry:
    log_message: str
    log_args: tuple[Any, ...]
    log_kwargs: dict[str, Any]
    module: str
    function: str
    line_number: int
    time: datetime


AccumulatedLogs = list[LogEntry]
