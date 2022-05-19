import asyncio
from typing import Callable
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from pybotx import (
    Bot,
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    HandlerCollector,
    IncomingMessage,
    UserKinds,
    lifespan_wrapper,
)

from pybotx_smart_logger import (
    BotXSmartLoggerMiddleware,
    make_smart_logger_decorator,
    make_smart_logger_exception_handler,
    smart_log,
    wrap_system_event,
)


async def test__botx_smart_logger_without_debug__called_error(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/hello", visible=False)
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler")
        raise ValueError("Test Error")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=False).dispatch,
        ],
    )

    message = incoming_message_factory(body="/hello")

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Hello from handler" in loguru_caplog.text
    assert "ValueError: Test Error" in loguru_caplog.text


async def test__botx_smart_logger_without_debug__empty_logs(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    trigger = AsyncMock()

    collector = HandlerCollector()

    @collector.command("/hello", visible=False)
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler")
        await trigger()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=False).dispatch,
        ],
    )

    message = incoming_message_factory(body="/hello")

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Hello from handler" not in loguru_caplog.text
    assert trigger.called


async def test__botx_smart_logger_with_debug__called_error(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/hello", visible=False)
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler")
        raise ValueError("Test Error")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=True).dispatch,
        ],
    )

    message = incoming_message_factory(body="/hello", raw_command={"Hello": "World"})

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Processing incoming_message:" in loguru_caplog.text
    assert "Hello from handler" in loguru_caplog.text
    assert "ValueError: Test Error" in loguru_caplog.text


async def test__botx_smart_logger_with_debug__succeed(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/hello", visible=False)
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=True).dispatch,
        ],
    )

    message = incoming_message_factory(body="/hello", raw_command={"Hello": "World"})

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Processing incoming_message:" in loguru_caplog.text
    assert "Hello from handler" in loguru_caplog.text


async def test__botx_smart_logger_with_debug__log_item(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/hello", visible=False)
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler", log_item="Log Item")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=True).dispatch,
        ],
    )

    message = incoming_message_factory(body="/hello", raw_command={"Hello": "World"})

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Processing incoming_message:" in loguru_caplog.text
    assert "Hello from handler" in loguru_caplog.text
    assert "Log Item" in loguru_caplog.text


async def test__botx_smart_logger_with_callable__succeed(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    trigger = AsyncMock()

    collector = HandlerCollector()

    @collector.command("/hello", visible=False)
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        smart_log("Hello from handler")

    async def func(_: IncomingMessage) -> bool:
        await trigger()
        return True

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=func).dispatch,
        ],
    )

    message = incoming_message_factory(body="/hello", raw_command={"Hello": "World"})

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Processing incoming_message:" in loguru_caplog.text
    assert "Hello from handler" in loguru_caplog.text
    assert trigger.called


async def test__smart_logger_decorator__succeed(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    trigger = AsyncMock()

    smart_logger_decorator = make_smart_logger_decorator(lambda task_name: True)

    @smart_logger_decorator
    async def background_task() -> None:
        await asyncio.sleep(1)
        smart_log("Hello from the background task")
        await trigger()

    collector = HandlerCollector()

    @collector.command("/hello", visible=False)
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        await background_task()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=True).dispatch,
        ],
    )

    message = incoming_message_factory(body="/hello")

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Hello from the background task" in loguru_caplog.text
    assert trigger.called


async def test__smart_logger_decorator__called_error(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    smart_logger_decorator = make_smart_logger_decorator(lambda task_name: False)

    @smart_logger_decorator
    async def background_task() -> None:
        smart_log("Hello from the background task")
        raise ValueError("Test Error")

    collector = HandlerCollector()

    @collector.command("/hello", visible=False)
    async def hello_handler(message: IncomingMessage, _: Bot) -> None:
        await background_task()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=True).dispatch,
        ],
    )

    message = incoming_message_factory(body="/hello")

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert "Hello from the background task" in loguru_caplog.text
    assert "ValueError: Test Error" in loguru_caplog.text


async def test__system_event_smart_logger_without_debug__error_called(
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
    bot_id: UUID,
    host: str,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    event = ChatCreatedEvent(
        sync_id=UUID("2c1a31d6-f47f-5f54-aee2-d0c526bb1d54"),
        bot=BotAccount(
            id=bot_id,
            host=host,
        ),
        chat_name="Feature-party",
        chat=Chat(
            id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
            type=ChatTypes.GROUP_CHAT,
        ),
        creator_id=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
        members=[
            ChatCreatedMember(
                is_admin=True,
                huid=bot_id,
                username="Feature bot",
                kind=UserKinds.BOT,
            ),
            ChatCreatedMember(
                is_admin=False,
                huid=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
                username="Ivanov Ivan Ivanovich",
                kind=UserKinds.CTS_USER,
            ),
        ],
        raw_command=None,
    )

    @collector.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, _: Bot) -> None:
        raise ValueError("Test Error")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=False).dispatch,
        ],
    )

    # - Act -
    with wrap_system_event(event, debug=False):
        async with lifespan_wrapper(built_bot) as bot:
            await bot.async_execute_bot_command(event)

    assert "ValueError: Test Error" in loguru_caplog.text


async def test__system_event_smart_logger_with_debug__error_called(
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
    bot_id: UUID,
    host: str,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    event = ChatCreatedEvent(
        sync_id=UUID("2c1a31d6-f47f-5f54-aee2-d0c526bb1d54"),
        bot=BotAccount(
            id=bot_id,
            host=host,
        ),
        chat_name="Feature-party",
        chat=Chat(
            id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
            type=ChatTypes.GROUP_CHAT,
        ),
        creator_id=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
        members=[
            ChatCreatedMember(
                is_admin=True,
                huid=bot_id,
                username="Feature bot",
                kind=UserKinds.BOT,
            ),
            ChatCreatedMember(
                is_admin=False,
                huid=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
                username="Ivanov Ivan Ivanovich",
                kind=UserKinds.CTS_USER,
            ),
        ],
        raw_command={"Hello": "World"},
    )

    @collector.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, _: Bot) -> None:
        raise ValueError("Test Error")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={
            Exception: make_smart_logger_exception_handler("Something went wrong"),
        },
        middlewares=[
            BotXSmartLoggerMiddleware(debug_enabled_for_message=False).dispatch,
        ],
    )

    # - Act -
    with wrap_system_event(event, debug=True):
        async with lifespan_wrapper(built_bot) as bot:
            await bot.async_execute_bot_command(event)

    assert "Processing incoming event:" in loguru_caplog.text
    assert "ValueError: Test Error" in loguru_caplog.text
