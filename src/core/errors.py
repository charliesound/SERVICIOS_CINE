from __future__ import annotations

from http import HTTPStatus
import logging
import traceback

from fastapi import HTTPException as FastAPIHTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("servicios_cine.error")


class ErrorDetail:
    code: str
    message: str
    details: dict
    request_id: str


def _should_expose_details(settings: object | None = None) -> bool:
    if settings is not None:
        from core.config import Settings

        if isinstance(settings, Settings):
            return settings.app_env in ("development", "test")
    from core.config import get_settings

    try:
        s = get_settings()
        return s.app_env in ("development", "test")
    except Exception:
        return True


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "")


def build_error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict | None = None,
    *,
    _expose_details: bool | None = None,
) -> dict:
    if _expose_details is None:
        _expose_details = _should_expose_details()
    normalized_details = details if isinstance(details, dict) else {}
    return {
        "error": {
            "code": code,
            "message": message,
            "details": normalized_details if _expose_details else {},
            "request_id": _get_request_id(request),
        }
    }


def _http_status_error_code(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).name.lower()
    except ValueError:
        return f"http_{status_code}"


def _http_status_message(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return str(status_code)


def _extract_http_error(exc: FastAPIHTTPException | StarletteHTTPException) -> tuple[str, str, dict]:
    details: dict = {}
    if isinstance(exc.detail, dict):
        details = dict(exc.detail)
        message = str(details.pop("message", _http_status_message(exc.status_code)))
    elif isinstance(exc.detail, str):
        message = exc.detail
    elif exc.detail is None:
        message = _http_status_message(exc.status_code)
    else:
        message = str(exc.detail)

    return _http_status_error_code(exc.status_code), message, details


async def http_exception_handler(
    request: Request,
    exc: FastAPIHTTPException | StarletteHTTPException,
) -> JSONResponse:
    code, message, details = _extract_http_error(exc)
    body = build_error_response(request, exc.status_code, code, message, details)
    return JSONResponse(status_code=exc.status_code, content=body)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    details = {"fields": errors}
    body = build_error_response(request, 422, "VALIDATION_ERROR", "Request validation failed", details)
    return JSONResponse(status_code=422, content=body)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    logger.error("Traceback:\n%s", "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

    body = build_error_response(
        request,
        500,
        "INTERNAL_ERROR",
        "An unexpected internal error occurred",
    )
    return JSONResponse(status_code=500, content=body)


def register_error_handlers(app, settings=None) -> None:
    app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
