import logging
from typing import Any, Callable, Dict, Generator, Optional
from uuid import UUID, uuid4

import pytest
from loguru import logger
from pybotx import (
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatTypes,
    IncomingMessage,
    UserDevice,
    UserSender,
)


@pytest.fixture
def bot_id() -> UUID:
    return UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")


@pytest.fixture
def chat_id() -> UUID:
    return UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517")


@pytest.fixture
def user_huid() -> UUID:
    return UUID("6d4b5b6e-ae32-4988-be5d-47baa7100c66")


@pytest.fixture
def host() -> str:
    return "cts.example.com"


@pytest.fixture
def bot_account(host: str, bot_id: UUID) -> BotAccountWithSecret:
    return BotAccountWithSecret(
        id=bot_id,
        host=host,
        secret_key="bee001",
    )


@pytest.fixture
def incoming_message_factory(
    bot_id: UUID,
    user_huid: UUID,
    chat_id: UUID,
    host: str,
) -> Callable[..., IncomingMessage]:
    def factory(
        *,
        body: str = "",
        raw_command: Optional[Dict[str, Any]] = None,
        ad_login: Optional[str] = None,
        ad_domain: Optional[str] = None,
    ) -> IncomingMessage:
        return IncomingMessage(
            bot=BotAccount(
                id=bot_id,
                host=host,
            ),
            sync_id=uuid4(),
            source_sync_id=None,
            body=body,
            data={},
            metadata={},
            sender=UserSender(
                huid=user_huid,
                ad_login=ad_login,
                ad_domain=ad_domain,
                username=None,
                is_chat_admin=True,
                is_chat_creator=True,
                device=UserDevice(
                    manufacturer=None,
                    device_name=None,
                    os=None,
                    pushes=None,
                    timezone=None,
                    permissions=None,
                    platform=None,
                    platform_package_id=None,
                    app_version=None,
                    locale=None,
                ),
            ),
            chat=Chat(
                id=chat_id,
                type=ChatTypes.PERSONAL_CHAT,
            ),
            raw_command=raw_command,
        )

    return factory


@pytest.fixture()
def loguru_caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[pytest.LogCaptureFixture, None, None]:
    # https://github.com/Delgan/loguru/issues/59

    class PropogateHandler(logging.Handler):  # noqa: WPS431
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)
