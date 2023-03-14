from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from loguru import logger

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import (
    get_grouping_enabled,
    set_debug_enabled,
    set_grouping_enabled,
)
from pybotx_smart_logger.logger import flush_accumulated_logs, smart_log


@asynccontextmanager
async def wrap_smart_logger(
    log_source: str,
    context_func: Callable[[], str],
    debug: bool = False,
    group: bool = False,
) -> AsyncGenerator[None, None]:
    set_debug_enabled(debug)
    set_grouping_enabled(group)

    smart_log(f"Processing `{log_source}`:\n{context_func()}")

    try:
        yield
    except Exception as exc:
        flush_accumulated_logs(log_levels.ERROR)
        logger.exception("")

        raise exc from None

    else:
        if get_grouping_enabled():
            flush_accumulated_logs(log_levels.INFO)
