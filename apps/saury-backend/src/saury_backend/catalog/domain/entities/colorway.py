import re
from dataclasses import dataclass, field
from typing import Self
from uuid import UUID, uuid7

from shared.domain.errors import ValidationError
from shared.domain.money import Money
from shared.domain.validation import require_text

from saury_backend.catalog.domain.entities.size_variant import SizeVariant
from saury_backend.catalog.domain.errors import SizeVariantNotFound
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize

COLORWAY_NAME_MAX_LENGTH = 100
SKU_MAX_LENGTH = 64
SKU_PATTERN = r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$"
COLOR_CODE_PATTERN = r"^#[0-9A-F]{6}$"
CASE_INSENSITIVE_SKU_PATTERN = r"(?i)^[A-Z0-9]+(?:-[A-Z0-9]+)*$"
CASE_INSENSITIVE_COLOR_CODE_PATTERN = r"(?i)^#[0-9A-F]{6}$"

_SKU_REGEX = re.compile(SKU_PATTERN)
_COLOR_CODE_REGEX = re.compile(COLOR_CODE_PATTERN)


def normalize_sku(sku: str) -> str:
    value = sku.strip().upper()
    if len(value) > SKU_MAX_LENGTH or not _SKU_REGEX.fullmatch(value):
        raise ValidationError(f"Invalid SKU: '{sku}'")
    return value


def _normalize_color_code(color_code: str) -> str:
    value = color_code.strip().upper()
    if not _COLOR_CODE_REGEX.fullmatch(value):
        raise ValidationError(f"Invalid color code: '{color_code}'")
    return value


@dataclass(slots=True)
class Colorway:
    id: UUID
    name: str
    color_code: str
    sku: str
    price_override: Money | None = None
    sizes: list[SizeVariant] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = require_text(self.name, field="name", max_length=COLORWAY_NAME_MAX_LENGTH)
        self.color_code = _normalize_color_code(self.color_code)
        self.sku = normalize_sku(self.sku)

    @classmethod
    def create(cls, name: str, color_code: str, sku: str, price_override: Money | None = None) -> Self:
        return cls(id=uuid7(), name=name, color_code=color_code, sku=sku, price_override=price_override)

    def update(self, name: str, color_code: str, sku: str, price_override: Money | None) -> None:
        self.name = require_text(name, field="name", max_length=COLORWAY_NAME_MAX_LENGTH)
        self.color_code = _normalize_color_code(color_code)
        self.sku = normalize_sku(sku)
        self.price_override = price_override

    def effective_price(self, base_price: Money) -> Money:
        return self.price_override or base_price

    def set_stock(self, size: ShoeSize, stock: int) -> SizeVariant:
        variant = self._find_size(size)
        if variant is None:
            variant = SizeVariant.create(size, stock)
            self.sizes.append(variant)
            self.sizes.sort(key=lambda item: item.size)
        else:
            variant.adjust_stock(stock)
        return variant

    def remove_size(self, size: ShoeSize) -> None:
        variant = self._find_size(size)
        if variant is None:
            raise SizeVariantNotFound(size)
        self.sizes.remove(variant)

    @property
    def has_sizes(self) -> bool:
        return bool(self.sizes)

    def _find_size(self, size: ShoeSize) -> SizeVariant | None:
        return next((variant for variant in self.sizes if variant.size == size), None)
