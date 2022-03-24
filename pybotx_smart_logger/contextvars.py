"""Contextvars for smart_logger."""

from contextvars import ContextVar
from typing import Dict, Optional

from pybotx_smart_logger.schemas import AccumulatedLogs, LogSource

_accumulated_logs_var: ContextVar[Optional[AccumulatedLogs]] = ContextVar(
    "accumulated_logs", default=None
)


def init_accumulated_logs() -> None:
    assert _accumulated_logs_var.get() is None
    _accumulated_logs_var.set([])


def get_accumulated_logs() -> AccumulatedLogs:
    accumulated_logs = _accumulated_logs_var.get()
    if accumulated_logs is None:
        accumulated_logs = []
        _accumulated_logs_var.set(accumulated_logs)

    return accumulated_logs


def clear_accumulated_logs() -> None:
    _accumulated_logs_var.set(None)


_debug_enabled_var: ContextVar[bool] = ContextVar("debug_enabled", default=False)


def get_debug_enabled() -> bool:
    return _debug_enabled_var.get()


def set_debug_enabled(new_value: bool) -> None:
    _debug_enabled_var.set(new_value)


_log_source_var: ContextVar[Optional[LogSource]] = ContextVar(
    "log_source_var", default=None
)


def get_log_source() -> Optional[LogSource]:
    return _log_source_var.get()


def set_log_source(log_source: LogSource) -> None:
    _log_source_var.set(log_source)


Headers = Dict[str, str]
_http_request_headers: ContextVar[Optional[Headers]] = ContextVar(
    "http_request_headers", default=None
)


def get_http_request_headers() -> Optional[Headers]:
    return _http_request_headers.get()


def set_http_request_headers(headers: Headers) -> None:
    _http_request_headers.set(headers)
