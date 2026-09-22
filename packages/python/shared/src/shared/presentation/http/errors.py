import logging
from collections.abc import Mapping, Sequence
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from shared.domain.errors import (
    CommonErrorCode,
    ConflictError,
    DomainError,
    ExternalServiceError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

logger = logging.getLogger(__name__)

REQUEST_VALIDATION_DETAIL = "Request validation failed"

_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    ValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
}

_CODE_BY_STATUS: dict[int, CommonErrorCode] = {
    status.HTTP_401_UNAUTHORIZED: CommonErrorCode.UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN: CommonErrorCode.FORBIDDEN,
    status.HTTP_404_NOT_FOUND: CommonErrorCode.NOT_FOUND,
    status.HTTP_409_CONFLICT: CommonErrorCode.CONFLICT,
    status.HTTP_422_UNPROCESSABLE_CONTENT: CommonErrorCode.VALIDATION_ERROR,
}

_LOCATIONS = {"body", "query", "path", "header", "cookie"}


def error_content(
    detail: str,
    code: str,
    params: Mapping[str, str | int] | None = None,
    errors: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    content: dict[str, Any] = {"detail": detail, "code": code, "params": dict(params or {})}
    if errors is not None:
        content["errors"] = list(errors)
    return content


def _primitive(value: Any) -> str | int | float | bool:
    return value if isinstance(value, str | int | float | bool) else str(value)


def _field_error(error: Mapping[str, Any]) -> dict[str, Any]:
    location = [str(part) for part in error.get("loc", ())]
    source = location[0] if location and location[0] in _LOCATIONS else "body"
    path = location[1:] if location and location[0] in _LOCATIONS else location
    context = error.get("ctx") or {}
    return {
        "field": ".".join(path),
        "location": source,
        "type": str(error.get("type", "value_error")),
        "ctx": {key: _primitive(value) for key, value in context.items()},
    }


async def _handle_domain_error(_: Request, error: DomainError) -> JSONResponse:
    status_code = next(
        (code for error_type, code in _STATUS_BY_ERROR.items() if isinstance(error, error_type)),
        status.HTTP_400_BAD_REQUEST,
    )
    content = error_content(str(error), str(error.code), error.params)
    if status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
        content["errors"] = []
    return JSONResponse(status_code=status_code, content=content)


async def _handle_request_validation(_: Request, error: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_content(
            REQUEST_VALIDATION_DETAIL,
            CommonErrorCode.VALIDATION_ERROR,
            errors=[_field_error(item) for item in error.errors()],
        ),
    )


async def _handle_http_exception(_: Request, error: StarletteHTTPException) -> JSONResponse:
    code = _CODE_BY_STATUS.get(error.status_code, CommonErrorCode.HTTP_ERROR)
    content = error_content(str(error.detail), code)
    if error.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
        content["errors"] = []
    return JSONResponse(status_code=error.status_code, content=content, headers=error.headers)


async def _handle_unexpected_error(_: Request, error: Exception) -> JSONResponse:
    logger.exception("Unhandled error", exc_info=error)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_content("Internal server error", CommonErrorCode.INTERNAL_ERROR),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _handle_domain_error)
    app.add_exception_handler(RequestValidationError, _handle_request_validation)
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)
    app.add_exception_handler(Exception, _handle_unexpected_error)
