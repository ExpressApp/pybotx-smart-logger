from typing import Any, Dict, Literal, Optional
from urllib.error import HTTPError

from httpx import AsyncClient, HTTPStatusError

from pybotx_smart_logger import smart_log

base_url = ""


class ResponseSchema:
    pass  # noqa: WPS420, WPS604


class RequestToAwesomeAPIError(Exception):
    pass  # noqa: WPS420, WPS604


class InvalidStatusCodeFromAwesomeAPIError(Exception):
    pass  # noqa: WPS420, WPS604


