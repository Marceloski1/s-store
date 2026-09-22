import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Self

from shared.domain.errors import CommonErrorCode, ValidationError

MONEY_DECIMAL_PLACES = 2
MONEY_MAX_AMOUNT = Decimal("99999999.99")
CURRENCY_PATTERN = r"^[A-Z]{3}$"

_CURRENCY_REGEX = re.compile(CURRENCY_PATTERN)
_CENT = Decimal(1).scaleb(-MONEY_DECIMAL_PLACES)


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not _CURRENCY_REGEX.fullmatch(self.currency):
            raise ValidationError(
                f"Invalid currency code: '{self.currency}'",
                code=CommonErrorCode.INVALID_CURRENCY,
                params={"currency": self.currency},
            )
        if not isinstance(self.amount, Decimal) or not self.amount.is_finite():
            raise ValidationError(
                f"Invalid amount: '{self.amount}'", code=CommonErrorCode.INVALID_AMOUNT, params={"value": str(self.amount)}
            )
        if self.amount < 0:
            raise ValidationError("amount must not be negative", code=CommonErrorCode.NEGATIVE_AMOUNT)
        if self.amount > MONEY_MAX_AMOUNT:
            raise ValidationError(
                f"amount must be at most {MONEY_MAX_AMOUNT}",
                code=CommonErrorCode.AMOUNT_TOO_LARGE,
                params={"max": str(MONEY_MAX_AMOUNT)},
            )
        if self.amount != self.amount.quantize(_CENT):
            raise ValidationError(
                f"amount must have at most {MONEY_DECIMAL_PLACES} decimal places",
                code=CommonErrorCode.TOO_MANY_DECIMALS,
                params={"max": MONEY_DECIMAL_PLACES},
            )
        object.__setattr__(self, "amount", self.amount.quantize(_CENT))

    @classmethod
    def of(cls, amount: Decimal | int | str, currency: str) -> Self:
        try:
            value = Decimal(amount)
        except InvalidOperation as error:
            raise ValidationError(
                f"Invalid amount: '{amount}'", code=CommonErrorCode.INVALID_AMOUNT, params={"value": str(amount)}
            ) from error
        return cls(amount=value, currency=currency)

    def __add__(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __lt__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount >= other.amount

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValidationError(
                f"Cannot operate on {self.currency} and {other.currency}",
                code=CommonErrorCode.MONEY_CURRENCY_MISMATCH,
                params={"expected": self.currency, "actual": other.currency},
            )
