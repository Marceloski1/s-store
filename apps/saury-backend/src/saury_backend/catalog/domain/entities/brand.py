from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid7

from shared.domain.slug import Slug
from shared.domain.validation import require_text

BRAND_NAME_MAX_LENGTH = 100


@dataclass(slots=True)
class Brand:
    id: UUID
    name: str
    slug: Slug

    def __post_init__(self) -> None:
        self.name = require_text(self.name, field="name", max_length=BRAND_NAME_MAX_LENGTH)

    @classmethod
    def create(cls, name: str, slug: Slug | None = None) -> Self:
        clean_name = require_text(name, field="name", max_length=BRAND_NAME_MAX_LENGTH)
        return cls(id=uuid7(), name=clean_name, slug=slug or Slug.from_text(clean_name))

    def update(self, name: str, slug: Slug | None = None) -> None:
        self.name = require_text(name, field="name", max_length=BRAND_NAME_MAX_LENGTH)
        self.slug = slug or Slug.from_text(self.name)
