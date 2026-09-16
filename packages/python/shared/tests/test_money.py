from collections.abc import Callable
from decimal import Decimal
from typing import Any, cast

import pytest

from shared.domain.errors import ValidationError
from shared.domain.money import MONEY_MAX_AMOUNT, Money


def test_normalizes_amount_to_two_decimal_places() -> None:
    money = Money.of("120", "USD")

    assert money.amount == Decimal("120.00")
    assert str(money.amount) == "120.00"
    assert str(money) == "120.00 USD"


def test_equal_amounts_with_different_scale_are_equal() -> None:
    assert Money.of("99.9", "EUR") == Money.of("99.90", "EUR")


def test_same_amount_in_different_currencies_is_not_equal() -> None:
    assert Money.of("10", "USD") != Money.of("10", "EUR")


def test_accepts_zero_and_max_amount() -> None:
    assert Money.of(0, "USD").amount == Decimal("0.00")
    assert Money(MONEY_MAX_AMOUNT, "USD").amount == MONEY_MAX_AMOUNT


@pytest.mark.parametrize(
    "amount",
    ["-0.01", "0.001", "100000000.00", "NaN", "Infinity", "abc"],
    ids=["negative", "three-decimals", "too-large", "nan", "infinity", "not-a-number"],
)
def test_rejects_invalid_amounts(amount: str) -> None:
    with pytest.raises(ValidationError):
        Money.of(amount, "USD")


def test_rejects_float_amounts() -> None:
    with pytest.raises(ValidationError):
        Money(cast(Any, 10.5), "USD")


@pytest.mark.parametrize("currency", ["", "usd", "US", "USDT", "U1D"])
def test_rejects_invalid_currency_codes(currency: str) -> None:
    with pytest.raises(ValidationError):
        Money.of("10", currency)


def test_adds_amounts_in_same_currency() -> None:
    assert Money.of("10.25", "USD") + Money.of("4.75", "USD") == Money.of("15", "USD")


def test_compares_amounts_in_same_currency() -> None:
    cheap = Money.of("10", "EUR")
    expensive = Money.of("20", "EUR")

    assert cheap < expensive
    assert cheap <= Money.of("10.00", "EUR")
    assert expensive > cheap
    assert expensive >= Money.of("20", "EUR")


@pytest.mark.parametrize(
    "operation",
    [
        lambda a, b: a + b,
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ],
    ids=["add", "lt", "le", "gt", "ge"],
)
def test_rejects_operations_between_currencies(operation: Callable[[Money, Money], object]) -> None:
    with pytest.raises(ValidationError):
        operation(Money.of("10", "USD"), Money.of("10", "EUR"))
