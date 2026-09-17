from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from shared.domain.money import CURRENCY_PATTERN
from shared.presentation.http.schemas import SlugStr

from saury_backend.catalog.domain.entities.brand import BRAND_NAME_MAX_LENGTH
from saury_backend.catalog.domain.entities.category import CATEGORY_NAME_MAX_LENGTH
from saury_backend.catalog.domain.entities.colorway import (
    CASE_INSENSITIVE_COLOR_CODE_PATTERN,
    CASE_INSENSITIVE_SKU_PATTERN,
    COLORWAY_NAME_MAX_LENGTH,
    SKU_MAX_LENGTH,
)
from saury_backend.catalog.domain.entities.image import IMAGE_ALT_MAX_LENGTH
from saury_backend.catalog.domain.entities.sneaker import SNEAKER_DESCRIPTION_MAX_LENGTH, SNEAKER_NAME_MAX_LENGTH
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus

CurrencyStr = Annotated[str, StringConstraints(pattern=CURRENCY_PATTERN)]
ColorCodeStr = Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, pattern=CASE_INSENSITIVE_COLOR_CODE_PATTERN)]
SkuStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_upper=True, pattern=CASE_INSENSITIVE_SKU_PATTERN, max_length=SKU_MAX_LENGTH
    ),
]
AltStr = Annotated[str, StringConstraints(strip_whitespace=True, max_length=IMAGE_ALT_MAX_LENGTH)]


class BrandRequest(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=BRAND_NAME_MAX_LENGTH)]
    slug: SlugStr | None = None


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class CategoryRequest(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=CATEGORY_NAME_MAX_LENGTH)]
    slug: SlugStr | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class SneakerRequest(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=SNEAKER_NAME_MAX_LENGTH)]
    description: Annotated[str, StringConstraints(max_length=SNEAKER_DESCRIPTION_MAX_LENGTH)] = ""
    brand_id: UUID
    category_id: UUID
    gender: Gender
    price: Annotated[Decimal, Field(ge=0)]
    currency: CurrencyStr
    release_date: date | None = None
    slug: SlugStr | None = None


class ColorwayRequest(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=COLORWAY_NAME_MAX_LENGTH)]
    color_code: ColorCodeStr
    sku: SkuStr
    price_override: Annotated[Decimal, Field(ge=0)] | None = None


class SizeStockRequest(BaseModel):
    stock: Annotated[int, Field(ge=0)]


class ImageOrderRequest(BaseModel):
    image_ids: list[UUID]


class MoneyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amount: Decimal
    currency: str


class SizeVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    size: Decimal
    stock: int


class ColorwayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    color_code: str
    sku: str
    price_override: MoneyResponse | None
    effective_price: MoneyResponse
    sizes: list[SizeVariantResponse]


class ImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_id: str
    url: str
    alt: str
    position: int
    is_primary: bool


class SneakerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str
    brand_id: UUID
    category_id: UUID
    gender: Gender
    base_price: MoneyResponse
    status: SneakerStatus
    release_date: date | None
    created_at: datetime
    updated_at: datetime
    colorways: list[ColorwayResponse]
    images: list[ImageResponse]
