"""Prints logs only if exception was raised while processing message."""

import inspect
from pprint import pformat
from typing import Any

from loguru import logger

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import (
    clear_accumulated_logs,
    get_accumulated_logs,
    get_debug_enabled,
)
from pybotx_smart_logger.output import attach_log_source
from pybotx_smart_logger.schemas import LogEntry
from pybotx_smart_logger.undefined import Undefined, undefined


def flush_log_entry(log_entry: LogEntry, log_level: str) -> None:
    patched_logger = logger.patch(
        lambda record: record.update(
            {
                "name": log_entry.module,
                "line": log_entry.line_number,
                "function": log_entry.function,
            }
        )
    )

    formatted_log_message = attach_log_source(log_entry.log_message)

    if isinstance(log_entry.log_item, Undefined):
        patched_logger.log(log_level, formatted_log_message)
    else:
        patched_logger.log(
            log_level, "{}\n{}", formatted_log_message, pformat(log_entry.log_item)
        )


def flush_accumulated_logs(log_level: str) -> None:
    for log_entry in get_accumulated_logs():
        flush_log_entry(log_entry, log_level)

    clear_accumulated_logs()


def smart_log(log_message: str, log_item: Any = undefined) -> None:
    caller_frame = inspect.stack()[1]
    log_entry = LogEntry(
        log_message=log_message,
        log_item=log_item,
        module=caller_frame.frame.f_globals["__name__"],
        function=caller_frame.function,
        line_number=caller_frame.lineno,
    )

    if get_debug_enabled():
        flush_log_entry(log_entry, log_levels.INFO)
    else:
        accumulated_logs = get_accumulated_logs()
        accumulated_logs.append(log_entry)
