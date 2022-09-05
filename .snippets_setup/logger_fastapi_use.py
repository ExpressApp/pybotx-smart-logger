from typing import Callable

from fastapi import FastAPI, Request

from pybotx_smart_logger import wrap_smart_logger


def pformat_str_request(request: Request) -> str:
    return ""


DEBUG = True

