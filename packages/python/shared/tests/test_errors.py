import pytest

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
from shared.domain.money import Money
from shared.domain.pagination import PageParams
from shared.domain.slug import Slug
from shared.domain.validation import require_text


@pytest.mark.parametrize(
    ("error_type", "code"),
    [
        (ValidationError, CommonErrorCode.VALIDATION_ERROR),
        (NotFoundError, CommonErrorCode.NOT_FOUND),
        (ConflictError, CommonErrorCode.CONFLICT),
        (UnauthorizedError, CommonErrorCode.UNAUTHORIZED),
        (ForbiddenError, CommonErrorCode.FORBIDDEN),
        (ExternalServiceError, CommonErrorCode.EXTERNAL_SERVICE_ERROR),
    ],
)
def test_error_families_have_generic_codes(error_type: type[DomainError], code: CommonErrorCode) -> None:
    error = error_type("boom")

    assert (str(error), error.code, error.params) == ("boom", code, {})


def test_errors_accept_specific_code_and_params() -> None:
    error = ValidationError("too long", code=CommonErrorCode.TEXT_TOO_LONG, params={"field": "name", "max": 10})

    assert error.code == CommonErrorCode.TEXT_TOO_LONG
    assert error.params == {"field": "name", "max": 10}


@pytest.mark.parametrize(
    ("action", "code", "params"),
    [
        (lambda: require_text("  ", field="name", max_length=5), CommonErrorCode.TEXT_REQUIRED, {"field": "name"}),
        (
            lambda: require_text("abcdef", field="name", max_length=5),
            CommonErrorCode.TEXT_TOO_LONG,
            {"field": "name", "max": 5},
        ),
        (lambda: Slug("Not A Slug"), CommonErrorCode.INVALID_SLUG, {"value": "Not A Slug"}),
        (lambda: Money.of("10", "usd"), CommonErrorCode.INVALID_CURRENCY, {"currency": "usd"}),
        (lambda: Money.of("abc", "USD"), CommonErrorCode.INVALID_AMOUNT, {"value": "abc"}),
        (lambda: Money.of("-1", "USD"), CommonErrorCode.NEGATIVE_AMOUNT, {}),
        (lambda: Money.of("1.234", "USD"), CommonErrorCode.TOO_MANY_DECIMALS, {"max": 2}),
        (
            lambda: Money.of("1", "USD") < Money.of("1", "EUR"),
            CommonErrorCode.MONEY_CURRENCY_MISMATCH,
            {"expected": "USD", "actual": "EUR"},
        ),
        (lambda: PageParams(page=0), CommonErrorCode.INVALID_PAGE, {}),
        (lambda: PageParams(size=500), CommonErrorCode.INVALID_PAGE_SIZE, {"max": 100}),
    ],
    ids=[
        "text-required",
        "text-too-long",
        "slug",
        "currency",
        "amount",
        "negative",
        "decimals",
        "currency-mismatch",
        "page",
        "page-size",
    ],
)
def test_shared_validations_raise_coded_errors(action, code: CommonErrorCode, params: dict[str, object]) -> None:
    with pytest.raises(ValidationError) as raised:
        action()

    assert (raised.value.code, raised.value.params) == (code, params)
