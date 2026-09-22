from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid7

from shared.domain.errors import ValidationError

from saury_backend.catalog.domain.error_codes import CatalogErrorCode
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize


def _require_stock(stock: int) -> int:
    if stock < 0:
        raise ValidationError("stock must not be negative", code=CatalogErrorCode.NEGATIVE_STOCK)
    return stock


@dataclass(slots=True)
class SizeVariant:
    id: UUID
    size: ShoeSize
    stock: int

    def __post_init__(self) -> None:
        self.stock = _require_stock(self.stock)

    @classmethod
    def create(cls, size: ShoeSize, stock: int) -> Self:
        return cls(id=uuid7(), size=size, stock=_require_stock(stock))

    def adjust_stock(self, stock: int) -> None:
        self.stock = _require_stock(stock)

    @property
    def in_stock(self) -> bool:
        return self.stock > 0
