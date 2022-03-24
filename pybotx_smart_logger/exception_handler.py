"""Exception handler for smart_logger.

Prints all accumulated logs and sends default error message.
"""

from typing import Awaitable, Callable

from pybotx import Bot, IncomingMessage
from pybotx_smartapp_rpc.models.errors import RPCError
from pybotx_smartapp_rpc.models.responses import RPCErrorResponse
from pybotx_smartapp_rpc.smartapp import SmartApp
from fastapi import Request
from loguru import logger
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import get_debug_enabled
from pybotx_smart_logger.logger import flush_accumulated_logs
from pybotx_smart_logger.output import (
    attach_log_source,
    log_system_event,
    log_incoming_http_request,
    log_incoming_message,
)


def make_smart_logger_exception_handler(
    error_text: str,
) -> Callable[[Exception, IncomingMessage], Awaitable[None]]:
    async def exception_handler(
        message: IncomingMessage, bot: Bot, exc: Exception
    ) -> None:
        if not get_debug_enabled():
            log_incoming_message(
                message.raw_command,
                "Error while processing incoming message:",
                log_levels.ERROR,
            )
            flush_accumulated_logs(log_levels.ERROR)

        logger.exception(attach_log_source(""))

        await bot.answer_message(error_text)

    return exception_handler


async def fastapi_exception_handler(request: Request, exc: Exception) -> Response:
    if not get_debug_enabled():
        flush_accumulated_logs(log_levels.ERROR)
        log_incoming_http_request(
            "Error while processing incoming http request",
            log_levels.ERROR,
        )

    return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def smartapp_exception_handler(
    exc: Exception,
    smartapp: SmartApp,
) -> RPCErrorResponse:
    if not get_debug_enabled():
        log_system_event(
            smartapp.event.raw_command,
            "Error while processing incoming SmartApp event:",
            log_levels.ERROR,
        )
        flush_accumulated_logs(log_levels.ERROR)

    logger.exception(attach_log_source(""))

    return RPCErrorResponse(
        errors=[RPCError(reason="Internal error", id=exc.__class__.__name__.upper())],
    )
