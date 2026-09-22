from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Self

from shared.domain.errors import ValidationError

from saury_backend.catalog.domain.error_codes import CatalogErrorCode

SHOE_SIZE_MAX = Decimal("99.5")
_SIZE_STEP = Decimal("0.5")


@dataclass(frozen=True, slots=True, order=True)
class ShoeSize:
    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal) or not self.value.is_finite():
            raise ValidationError(
                f"Invalid shoe size: '{self.value}'",
                code=CatalogErrorCode.INVALID_SHOE_SIZE,
                params={"value": str(self.value), "max": str(SHOE_SIZE_MAX)},
            )
        if not 0 < self.value <= SHOE_SIZE_MAX or self.value % _SIZE_STEP != 0:
            raise ValidationError(
                f"Shoe size must be a positive EU size in steps of 0.5 up to {SHOE_SIZE_MAX}",
                code=CatalogErrorCode.INVALID_SHOE_SIZE,
                params={"value": str(self.value), "max": str(SHOE_SIZE_MAX)},
            )
        object.__setattr__(self, "value", self.value.quantize(Decimal("0.1")))

    @classmethod
    def of(cls, value: Decimal | int | str) -> Self:
        try:
            return cls(Decimal(value))
        except InvalidOperation as error:
            raise ValidationError(
                f"Invalid shoe size: '{value}'",
                code=CatalogErrorCode.INVALID_SHOE_SIZE,
                params={"value": str(value), "max": str(SHOE_SIZE_MAX)},
            ) from error

    def __str__(self) -> str:
        return str(self.value.normalize()) if self.value % 1 else str(int(self.value))
