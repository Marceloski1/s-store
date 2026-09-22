from collections.abc import Mapping
from enum import StrEnum

type ErrorParams = Mapping[str, str | int]


class CommonErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    TEXT_REQUIRED = "TEXT_REQUIRED"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    INVALID_SLUG = "INVALID_SLUG"
    INVALID_CURRENCY = "INVALID_CURRENCY"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    NEGATIVE_AMOUNT = "NEGATIVE_AMOUNT"
    AMOUNT_TOO_LARGE = "AMOUNT_TOO_LARGE"
    TOO_MANY_DECIMALS = "TOO_MANY_DECIMALS"
    MONEY_CURRENCY_MISMATCH = "MONEY_CURRENCY_MISMATCH"
    INVALID_PAGE = "INVALID_PAGE"
    INVALID_PAGE_SIZE = "INVALID_PAGE_SIZE"


class DomainError(Exception):
    code: str = CommonErrorCode.VALIDATION_ERROR

    def __init__(self, message: str, *, code: str | None = None, params: ErrorParams | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code
        self.params: dict[str, str | int] = dict(params or {})


class ValidationError(DomainError):
    code = CommonErrorCode.VALIDATION_ERROR


class NotFoundError(DomainError):
    code = CommonErrorCode.NOT_FOUND


class ConflictError(DomainError):
    code = CommonErrorCode.CONFLICT


class UnauthorizedError(DomainError):
    code = CommonErrorCode.UNAUTHORIZED


class ForbiddenError(DomainError):
    code = CommonErrorCode.FORBIDDEN


class ExternalServiceError(DomainError):
    code = CommonErrorCode.EXTERNAL_SERVICE_ERROR
