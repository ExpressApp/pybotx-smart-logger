"""Schemas for smart logger internals."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, List
from uuid import UUID

from pybotx.models.commands import SystemEvent


class LogSourceType(str, Enum):
    USER_MESSAGE = "USER_MESSAGE"
    ASYNCIO_TASK = "ASYNCIO_TASK"
    HTTP_HANDLER = "HTTP_HANDLER"
    SYSTEM_EVENT = "SYSTEM_EVENT"


@dataclass
class LogSource:
    source_type: LogSourceType
    source_context: Any

    @classmethod
    def from_user_message(cls, user_huid: UUID) -> LogSource:
        return cls(source_type=LogSourceType.USER_MESSAGE, source_context=user_huid)

    @classmethod
    def from_asyncio_task(cls, task_name: str) -> LogSource:
        return cls(source_type=LogSourceType.ASYNCIO_TASK, source_context=task_name)

    @classmethod
    def from_http_request(cls, method: str, url: str) -> LogSource:
        return cls(source_type=LogSourceType.HTTP_HANDLER, source_context=(method, url))

    @classmethod
    def from_system_event(cls, event: SystemEvent) -> LogSource:
        return cls(
            source_type=LogSourceType.SYSTEM_EVENT,
            source_context=(event.bot.id, event.__class__.__name__),
        )


@dataclass
class LogEntry:
    log_message: str
    log_item: Any
    module: str
    function: str
    line_number: int


AccumulatedLogs = List[LogEntry]
