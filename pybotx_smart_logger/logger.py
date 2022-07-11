"""Prints logs only if exception was raised while processing message."""

import inspect
from typing import Any

from loguru import logger

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import (
    clear_accumulated_logs,
    get_accumulated_logs,
    get_debug_enabled,
)
from pybotx_smart_logger.schemas import LogEntry


def flush_log_entry(log_entry: LogEntry, log_level: str) -> None:
    patched_logger = logger.patch(
        lambda record: record.update(
            {
                "name": log_entry.module,
                "line": log_entry.line_number,
                "function": log_entry.function,
            },
        ),
    )

    patched_logger.log(
        log_level,
        log_entry.log_message,
        *log_entry.log_args,
        **log_entry.log_kwargs,
    )


def flush_accumulated_logs(log_level: str) -> None:
    for log_entry in get_accumulated_logs():
        flush_log_entry(log_entry, log_level)

    clear_accumulated_logs()


def smart_log(log_message: str, *args: Any, **kwargs: Any) -> None:
    caller_frame = inspect.stack()[1]
    log_entry = LogEntry(
        log_message=log_message,
        log_args=args,
        log_kwargs=kwargs,
        module=caller_frame.frame.f_globals["__name__"],
        function=caller_frame.function,
        line_number=caller_frame.lineno,
    )

    if get_debug_enabled():
        flush_log_entry(log_entry, log_levels.INFO)
    else:
        accumulated_logs = get_accumulated_logs()
        accumulated_logs.append(log_entry)
