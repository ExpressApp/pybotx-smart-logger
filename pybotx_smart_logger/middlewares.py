"""Middlewares for smart logger."""

from typing import Awaitable, Callable, Union

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc
from fastapi import Request

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import (
    init_accumulated_logs,
    set_debug_enabled,
    set_http_request_headers,
    set_log_source,
)
from pybotx_smart_logger.output import log_incoming_http_request, log_incoming_message
from pybotx_smart_logger.schemas import LogSource


class BotXSmartLoggerMiddleware:
    def __init__(
        self,
        debug_enabled_for_message: Union[
            Callable[[IncomingMessage], Awaitable[bool]], bool
        ],
    ) -> None:
        self._debug_enabled_for_message = debug_enabled_for_message

    async def dispatch(
        self, message: IncomingMessage, bot: Bot, call_next: IncomingMessageHandlerFunc
    ) -> None:
        set_log_source(LogSource.from_user_message(message.sender.huid))

        if isinstance(self._debug_enabled_for_message, bool):
            debug_enabled = self._debug_enabled_for_message
        else:
            debug_enabled = await self._debug_enabled_for_message(message)

        set_debug_enabled(debug_enabled)

        if debug_enabled:
            log_incoming_message(
                message.raw_command,
                "Processing incoming_message:",
                log_levels.INFO,
            )

        await call_next(message, bot)


class FastApiSmartLoggerMiddleware:
    def __init__(
        self,
        *,
        debug_enabled: bool = False,
    ) -> None:
        self._debug_enabled = debug_enabled

    async def __call__(self, request: Request, call_next: Callable) -> None:
        # In pybotx handlers runs in a separate asyncio task.
        # If the contextvar variable is set in a child task, the parent task
        # don't know about it. Here we init the log storage with an empty list.
        # So when the child task will append it, we will find it out.
        init_accumulated_logs()

        method = request.method
        url = str(request.url)
        headers = dict(request.headers)

        set_http_request_headers(headers)
        set_log_source(LogSource.from_http_request(method, url))

        set_debug_enabled(self._debug_enabled)

        if self._debug_enabled:
            log_incoming_http_request(
                "Processing incoming http request",
                log_levels.INFO,
            )

        return await call_next(request)
