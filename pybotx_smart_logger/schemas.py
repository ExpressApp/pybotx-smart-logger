"""Schemas for smart logger internals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List


@dataclass
class LogEntry:
    log_message: str
    log_item: Any
    module: str
    function: str
    line_number: int


AccumulatedLogs = List[LogEntry]
