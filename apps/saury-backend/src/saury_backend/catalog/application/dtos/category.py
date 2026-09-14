from dataclasses import dataclass
from typing import Self
from uuid import UUID

from saury_backend.catalog.domain.entities.category import Category


@dataclass(frozen=True, slots=True)
class CategoryDTO:
    id: UUID
    name: str
    slug: str

    @classmethod
    def from_entity(cls, category: Category) -> Self:
        return cls(id=category.id, name=category.name, slug=category.slug.value)


@dataclass(frozen=True, slots=True)
class CreateCategoryCommand:
    name: str
    slug: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateCategoryCommand:
    category_id: UUID
    name: str
    slug: str | None = None
