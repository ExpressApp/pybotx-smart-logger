from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from loguru import logger

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import get_debug_enabled, set_debug_enabled
from pybotx_smart_logger.logger import flush_accumulated_logs


@asynccontextmanager
async def wrap_smart_logger(
    log_source: str,
    context_func: Callable[[], str],
    debug: bool = False,
) -> AsyncGenerator[None, None]:
    set_debug_enabled(debug)

    if get_debug_enabled():
        context = context_func()
        logger.info("Processing `{}`:\n{}", log_source, context)

    try:
        yield
    except Exception as exc:
        if not get_debug_enabled():
            context = context_func()
            logger.error("Error while processing `{}`:\n{}", log_source, context)

        flush_accumulated_logs(log_levels.ERROR)

        logger.exception("")

        raise exc from None
