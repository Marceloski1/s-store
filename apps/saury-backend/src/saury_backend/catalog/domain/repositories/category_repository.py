from typing import Protocol
from uuid import UUID

from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.domain.entities.category import Category


class CategoryRepository(Protocol):
    async def save(self, category: Category) -> None: ...

    async def get(self, category_id: UUID) -> Category | None: ...

    async def get_by_slug(self, slug: Slug) -> Category | None: ...

    async def paginate(self, params: PageParams) -> Page[Category]: ...

    async def delete(self, category: Category) -> None: ...
