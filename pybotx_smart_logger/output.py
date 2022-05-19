"""Helpers for printing log messages."""

from pprint import pformat
from typing import Any, Dict, Optional

from loguru import logger
from pybotx.logger import trim_file_data_in_incoming_json

from pybotx_smart_logger.contextvars import get_http_request_headers, get_log_source
from pybotx_smart_logger.schemas import LogSourceType

MAX_FILE_CONTENT_LENGTH = 32


def attach_log_source(log_message: str) -> str:
    raw_log_source = get_log_source()

    if raw_log_source is None:  # pragma: no cover
        log_source = "<missing log source>"
    elif raw_log_source.source_type == LogSourceType.USER_MESSAGE.value:
        log_source = f"user '{raw_log_source.source_context}'"
    elif raw_log_source.source_type == LogSourceType.ASYNCIO_TASK.value:
        log_source = f"task '{raw_log_source.source_context}'"
    elif raw_log_source.source_type == LogSourceType.HTTP_HANDLER.value:
        method, url = raw_log_source.source_context
        log_source = f"HTTP {method} {url}"
    elif raw_log_source.source_type == LogSourceType.SYSTEM_EVENT.value:
        bot_id, event = raw_log_source.source_context
        log_source = f"event {event} to bot '{bot_id}'"
    else:
        raise NotImplementedError(
            f"Unsupported log source: `{raw_log_source}`",
        )  # pragma: no cover

    return f"[{log_source}] {log_message}"


def log_incoming_message(
    raw_command: Optional[Dict[str, Any]],
    title: str,
    log_level: str,
) -> None:
    if raw_command is None:
        logger.warning("Empty `raw_command`")
        return

    trimmed_raw_command = trim_file_data_in_incoming_json(raw_command)
    logger.log(log_level, "{}\n{}", title, pformat(trimmed_raw_command))


def log_system_event(
    raw_command: Optional[Dict[str, Any]],
    title: str,
    log_level: str,
) -> None:
    if raw_command is None:
        logger.warning("Empty `raw_command`")
        return

    logger.log(log_level, "{}\n{}", title, pformat(raw_command))


def log_incoming_http_request(
    title: str,
    log_level: str,
) -> None:
    log_source = get_log_source()
    assert log_source is not None
    method, url = log_source.source_context

    headers = get_http_request_headers()
    assert headers is not None

    formatted_headers = "\n".join(
        [f"{key}: {value}" for key, value in headers.items()],
    )
    logger.log(
        log_level,
        "{}:\nHTTP {} {}\nHeaders:\n{}",
        title,
        method,
        url,
        formatted_headers,
    )
