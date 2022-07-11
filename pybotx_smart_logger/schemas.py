"""Schemas for smart logger internals."""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class LogEntry:
    log_message: str
    log_args: Tuple[Any, ...]
    log_kwargs: Dict[str, Any]
    module: str
    function: str
    line_number: int


AccumulatedLogs = List[LogEntry]
