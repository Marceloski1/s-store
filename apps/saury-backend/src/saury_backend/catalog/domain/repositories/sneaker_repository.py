from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from shared.domain.errors import CommonErrorCode, ValidationError
from shared.domain.money import Money
from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.error_codes import CatalogErrorCode
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus

SEARCH_QUERY_MAX_LENGTH = 100


class SneakerSort(StrEnum):
    NAME = "NAME"
    PRICE = "PRICE"
    RELEASE_DATE = "RELEASE_DATE"
    CREATED_AT = "CREATED_AT"


@dataclass(frozen=True, slots=True)
class SneakerFilters:
    brands: tuple[Slug, ...] = ()
    categories: tuple[Slug, ...] = ()
    genders: tuple[Gender, ...] = ()
    status: SneakerStatus | None = None
    sizes: tuple[ShoeSize, ...] = ()
    colors: tuple[str, ...] = ()
    min_price: Money | None = None
    max_price: Money | None = None
    in_stock: bool = False
    q: str | None = None
    sort: SneakerSort = SneakerSort.CREATED_AT
    descending: bool = False

    def __post_init__(self) -> None:
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValidationError(
                "min_price must be less than or equal to max_price", code=CatalogErrorCode.INVALID_PRICE_RANGE
            )
        if self.q is not None:
            query = self.q.strip()
            if len(query) > SEARCH_QUERY_MAX_LENGTH:
                raise ValidationError(
                    f"q must be at most {SEARCH_QUERY_MAX_LENGTH} characters",
                    code=CommonErrorCode.TEXT_TOO_LONG,
                    params={"field": "q", "max": SEARCH_QUERY_MAX_LENGTH},
                )
            object.__setattr__(self, "q", query or None)

    @property
    def price_currency(self) -> str | None:
        price = self.min_price or self.max_price
        return price.currency if price is not None else None


@dataclass(frozen=True, slots=True)
class FacetCount:
    value: str
    label: str
    count: int


@dataclass(frozen=True, slots=True)
class CatalogFacets:
    brands: list[FacetCount]
    categories: list[FacetCount]
    genders: list[FacetCount]
    sizes: list[FacetCount]
    colors: list[FacetCount]
    currencies: list[str]


class SneakerRepository(Protocol):
    async def save(self, sneaker: Sneaker) -> None: ...

    async def get(self, sneaker_id: UUID) -> Sneaker | None: ...

    async def get_by_slug(self, slug: Slug) -> Sneaker | None: ...

    async def find_sku_owner(self, sku: str) -> UUID | None: ...

    async def find_reference_owner(self, reference: str) -> UUID | None: ...

    async def paginate(self, filters: SneakerFilters, params: PageParams) -> Page[Sneaker]: ...

    async def facets(self, status: SneakerStatus | None) -> CatalogFacets: ...

    async def delete(self, sneaker: Sneaker) -> None: ...

    async def exists_for_brand(self, brand_id: UUID) -> bool: ...

    async def exists_for_category(self, category_id: UUID) -> bool: ...
