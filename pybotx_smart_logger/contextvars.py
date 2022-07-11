"""Contextvars for smart_logger."""

from contextvars import ContextVar
from typing import Optional

from pybotx_smart_logger.schemas import AccumulatedLogs

_accumulated_logs_var: ContextVar[Optional[AccumulatedLogs]] = ContextVar(
    "accumulated_logs",
    default=None,
)


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
