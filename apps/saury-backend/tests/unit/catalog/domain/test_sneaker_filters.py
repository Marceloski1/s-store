import pytest
from shared.domain.errors import ValidationError
from shared.domain.money import Money

from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerFilters


def test_price_currency_comes_from_price_bounds() -> None:
    assert SneakerFilters(min_price=Money.of("50", "EUR")).price_currency == "EUR"
    assert SneakerFilters(max_price=Money.of("90", "USD")).price_currency == "USD"
    assert SneakerFilters().price_currency is None


def test_rejects_min_price_greater_than_max_price() -> None:
    with pytest.raises(ValidationError):
        SneakerFilters(min_price=Money.of("100", "USD"), max_price=Money.of("50", "USD"))


def test_rejects_price_bounds_in_different_currencies() -> None:
    with pytest.raises(ValidationError):
        SneakerFilters(min_price=Money.of("10", "USD"), max_price=Money.of("50", "EUR"))


def test_blank_search_query_is_ignored() -> None:
    assert SneakerFilters(q="   ").q is None
    assert SneakerFilters(q=" jordan ").q == "jordan"


def test_rejects_too_long_search_query() -> None:
    with pytest.raises(ValidationError):
        SneakerFilters(q="a" * 101)
