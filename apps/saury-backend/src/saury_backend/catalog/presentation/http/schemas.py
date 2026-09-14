from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints
from shared.presentation.http.schemas import SlugStr

from saury_backend.catalog.domain.entities.brand import BRAND_NAME_MAX_LENGTH
from saury_backend.catalog.domain.entities.category import CATEGORY_NAME_MAX_LENGTH


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
