from typing import Callable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pybotx import BotAccountWithSecret, IncomingMessage

from pybotx_smart_logger import (
    FastApiSmartLoggerMiddleware,
    fastapi_exception_handler,
    smart_log,
)


async def test__fastapi_smart_logger_without_debug__error_called(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    application = FastAPI(title="Test", openapi_url=None)
    application.middleware("http")(FastApiSmartLoggerMiddleware(debug_enabled=False))
    application.add_exception_handler(Exception, fastapi_exception_handler)

    @application.get("/hello")
    async def hello_handler() -> None:
        smart_log("Hello from FastAPI handler")
        raise ValueError("Test Error")

    # - Act -
    with pytest.raises(ValueError):
        with TestClient(application) as client:
            client.get("/hello")

    # - Assert -
    assert "Hello from FastAPI handler" in loguru_caplog.text
    assert "ValueError: Test Error" in loguru_caplog.text


async def test__fastapi_smart_logger_with_debug__error_called(
    bot_account: BotAccountWithSecret,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    application = FastAPI(title="Test", openapi_url=None)
    application.middleware("http")(FastApiSmartLoggerMiddleware(debug_enabled=True))
    application.add_exception_handler(Exception, fastapi_exception_handler)

    @application.get("/hello")
    async def hello_handler() -> None:
        raise ValueError("Test Error")

    # - Act -
    with pytest.raises(ValueError):
        with TestClient(application) as client:
            client.get("/hello")

    # - Assert -
    assert "Processing incoming http request:" in loguru_caplog.text
    assert "ValueError: Test Error" in loguru_caplog.text
