from typing import Optional

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc

from pybotx_smart_logger import wrap_smart_logger


def format_raw_command(command: Optional[dict]) -> str:
    return str(command)


