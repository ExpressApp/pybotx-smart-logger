from contextlib import contextmanager
from typing import Iterator

from loguru import logger
from pybotx.models.commands import SystemEvent

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import set_debug_enabled, set_log_source
from pybotx_smart_logger.logger import flush_accumulated_logs
from pybotx_smart_logger.output import attach_log_source, log_system_event
from pybotx_smart_logger.schemas import LogSource


@contextmanager
def wrap_system_event(
    event: SystemEvent,
    debug: bool = False,
) -> Iterator[None]:
    set_debug_enabled(debug)
    set_log_source(LogSource.from_system_event(event))

    if debug:
        log_system_event(
            event.raw_command,
            "Processing incoming event:",
            log_levels.INFO,
        )

    try:
        yield
    except Exception:
        if not debug:
            log_system_event(
                event.raw_command,
                "Error while processing incoming SmartApp event:",
                log_levels.ERROR,
            )
            flush_accumulated_logs(log_levels.ERROR)

        logger.exception(attach_log_source(""))
