import asyncio
from pprint import pformat
from typing import Any, Callable
from unittest.mock import AsyncMock

import pytest
from loguru import logger
from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    IncomingMessageHandlerFunc,
    lifespan_wrapper,
)
from pybotx.logger import trim_file_data_in_incoming_json

from pybotx_smart_logger import smart_log, wrap_smart_logger


async def test__wrap_smart_logger__debug_off__no_error(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    trigger = AsyncMock()
    collector = HandlerCollector()

    def format_raw_command(raw_command: dict[str, Any] | None) -> str:
        if raw_command is None:
            logger.warning("Empty `raw_command`")
            return ""

        trimmed_raw_command = trim_file_data_in_incoming_json(raw_command)
        return pformat(trimmed_raw_command)

    async def wrap_smart_logger_middleware(
        message: IncomingMessage,
        bot: Bot,
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        async with wrap_smart_logger(
            "Incoming message",
            lambda: format_raw_command(message.raw_command),
            debug=False,
        ):
            await call_next(message, bot)

    @collector.command(
        "/hello",
        visible=False,
        middlewares=[wrap_smart_logger_middleware],
    )
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler")
        await trigger()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
    )

    message = incoming_message_factory(body="/hello", raw_command={"Hello": "World"})

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Hello from handler" not in loguru_caplog.text
    assert trigger.called


async def test__wrap_smart_logger__debug_on__no_error(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    def format_raw_command(raw_command: dict[str, Any] | None) -> str:
        if raw_command is None:
            logger.warning("Empty `raw_command`")
            return ""

        trimmed_raw_command = trim_file_data_in_incoming_json(raw_command)
        return pformat(trimmed_raw_command)

    async def wrap_smart_logger_middleware(
        message: IncomingMessage,
        bot: Bot,
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        async with wrap_smart_logger(
            "Incoming message",
            lambda: format_raw_command(message.raw_command),
            debug=True,
        ):
            await call_next(message, bot)

    @collector.command(
        "/hello",
        visible=False,
        middlewares=[wrap_smart_logger_middleware],
    )
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
    )

    message = incoming_message_factory(body="/hello", raw_command={"Hello": "World"})

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Hello from handler" in loguru_caplog.text


async def test__wrap_smart_logger__debug_off__error_occured(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    def format_raw_command(raw_command: dict[str, Any] | None) -> str:
        if raw_command is None:
            logger.warning("Empty `raw_command`")
            return ""

        trimmed_raw_command = trim_file_data_in_incoming_json(raw_command)
        return pformat(trimmed_raw_command)

    async def wrap_smart_logger_middleware(
        message: IncomingMessage,
        bot: Bot,
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        async with wrap_smart_logger(
            "Incoming message",
            lambda: format_raw_command(message.raw_command),
            debug=False,
        ):
            await call_next(message, bot)

    @collector.command(
        "/hello",
        visible=False,
        middlewares=[wrap_smart_logger_middleware],
    )
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler")
        raise ValueError("Test Error")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
    )

    message = incoming_message_factory(body="/hello", raw_command={"Hello": "World"})

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError):
            await bot.async_execute_bot_command(message)

    # - Assert -
    assert "ValueError: Test Error" in loguru_caplog.text
    assert "Hello from handler" in loguru_caplog.text


async def test__wrap_smart_logger__debug_on__error_occured(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    def format_raw_command(raw_command: dict[str, Any] | None) -> str:
        if raw_command is None:
            logger.warning("Empty `raw_command`")
            return ""

        trimmed_raw_command = trim_file_data_in_incoming_json(raw_command)
        return pformat(trimmed_raw_command)

    async def wrap_smart_logger_middleware(
        message: IncomingMessage,
        bot: Bot,
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        async with wrap_smart_logger(
            "Incoming message",
            lambda: format_raw_command(message.raw_command),
            debug=True,
        ):
            await call_next(message, bot)

    @collector.command(
        "/hello",
        visible=False,
        middlewares=[wrap_smart_logger_middleware],
    )
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler", log_item="Log Item")
        raise ValueError("Test Error")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
    )

    message = incoming_message_factory(body="/hello", raw_command={"Hello": "World"})

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError):
            await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Hello from handler" in loguru_caplog.text
    assert "ValueError: Test Error" in loguru_caplog.text


async def test__wrap_smart_logger__group_on__no_error(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    def format_raw_command(raw_command: dict[str, Any] | None) -> str:
        if raw_command is None:
            logger.warning("Empty `raw_command`")
            return ""

        trimmed_raw_command = trim_file_data_in_incoming_json(raw_command)
        return pformat(trimmed_raw_command)

    async def wrap_smart_logger_middleware(
        message: IncomingMessage,
        bot: Bot,
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        async with wrap_smart_logger(
            "Incoming message",
            lambda: format_raw_command(message.raw_command),
            debug=True,
            group=True,
        ):
            await call_next(message, bot)

    @collector.command(
        "/hello",
        visible=False,
        middlewares=[wrap_smart_logger_middleware],
    )
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log(f"First hello from {message.body}")
        await asyncio.sleep(1)
        smart_log(f"Second hello from {message.body}")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
    )

    message1 = incoming_message_factory(
        body="/hello one",
        raw_command={"Hello": "World"},
    )
    message2 = incoming_message_factory(
        body="/hello two",
        raw_command={"Hello": "World"},
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        message1_task = bot.async_execute_bot_command(message1)
        await asyncio.sleep(0.1)  # Start first command processing

        await asyncio.gather(message1_task, bot.async_execute_bot_command(message2))

    # - Assert -
    logs_positions = [
        loguru_caplog.text.find("First hello from /hello one"),
        loguru_caplog.text.find("Second hello from /hello one"),
        loguru_caplog.text.find("First hello from /hello two"),
        loguru_caplog.text.find("Second hello from /hello two"),
    ]

    assert logs_positions == sorted(logs_positions)
