from enum import StrEnum

from fastapi import status
from pydantic import BaseModel, Field
from shared.domain.errors import CommonErrorCode

from saury_backend.catalog.domain.error_codes import CatalogErrorCode
from saury_backend.identity.domain.error_codes import IdentityErrorCode

_FEATURE_CODES: tuple[type[StrEnum], ...] = (CommonErrorCode, CatalogErrorCode, IdentityErrorCode)


def _merge_codes(enums: tuple[type[StrEnum], ...]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for enum in enums:
        for member in enum:
            if member.value in merged:
                raise ValueError(f"Duplicated error code: {member.value}")
            merged[member.value] = member.value
    return merged


ErrorCode = StrEnum("ErrorCode", _merge_codes(_FEATURE_CODES))


class ErrorResponse(BaseModel):
    detail: str
    code: ErrorCode
    params: dict[str, str | int] = Field(default_factory=dict)


class FieldError(BaseModel):
    field: str
    location: str
    type: str
    ctx: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ValidationErrorResponse(ErrorResponse):
    errors: list[FieldError] = Field(default_factory=list)


NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}
CONFLICT_RESPONSE = {status.HTTP_409_CONFLICT: {"model": ErrorResponse}}
UNPROCESSABLE_RESPONSE = {status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponse}}
UNAUTHORIZED_RESPONSE = {status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse}}
FORBIDDEN_RESPONSE = {status.HTTP_403_FORBIDDEN: {"model": ErrorResponse}}
BAD_GATEWAY_RESPONSE = {status.HTTP_502_BAD_GATEWAY: {"model": ErrorResponse}}
AUTH_RESPONSES = UNAUTHORIZED_RESPONSE | FORBIDDEN_RESPONSE
DEFAULT_ERROR_RESPONSES = UNPROCESSABLE_RESPONSE
