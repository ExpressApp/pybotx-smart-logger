from uuid import uuid4

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    IncomingMessageHandlerFunc,
)


async def smart_logger_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    return  # noqa: WPS324


collector = HandlerCollector()
BOT_CREDENTIALS = BotAccountWithSecret(  # noqa: S106
    secret_key="",
    host="",
    id=uuid4(),
)


