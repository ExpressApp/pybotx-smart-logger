"""Module for wrapping asyncio tasks with smart logger."""

from functools import wraps
from typing import Callable

from loguru import logger

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import (
    clear_accumulated_logs,
    set_debug_enabled,
    set_log_source,
)
from pybotx_smart_logger.logger import flush_accumulated_logs
from pybotx_smart_logger.schemas import LogSource


def make_smart_logger_decorator(
    debug_enabled_for_task: Callable[[str], bool]
) -> Callable:
    def decorator(func):  # type: ignore
        @wraps(func)
        async def wrapper(*args, **kwargs):  # type: ignore
            func_name = func.__name__

            set_debug_enabled(debug_enabled_for_task(func_name))
            set_log_source(LogSource.from_asyncio_task(func_name))
            clear_accumulated_logs()

            try:
                return await func(*args, **kwargs)
            except Exception:
                logger.error(f"An error happened in task '{func_name}':")
                flush_accumulated_logs(log_levels.ERROR)
                logger.exception("")

        return wrapper

    return decorator
