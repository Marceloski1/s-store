from dataclasses import dataclass
from typing import Self
from uuid import UUID

from saury_backend.catalog.domain.entities.brand import Brand


@dataclass(frozen=True, slots=True)
class BrandDTO:
    id: UUID
    name: str
    slug: str

    @classmethod
    def from_entity(cls, brand: Brand) -> Self:
        return cls(id=brand.id, name=brand.name, slug=brand.slug.value)


@dataclass(frozen=True, slots=True)
class CreateBrandCommand:
    name: str
    slug: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateBrandCommand:
    brand_id: UUID
    name: str
    slug: str | None = None
