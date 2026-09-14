from typing import Protocol
from uuid import UUID

from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.domain.entities.brand import Brand


class BrandRepository(Protocol):
    async def save(self, brand: Brand) -> None: ...

    async def get(self, brand_id: UUID) -> Brand | None: ...

    async def get_by_slug(self, slug: Slug) -> Brand | None: ...

    async def paginate(self, params: PageParams) -> Page[Brand]: ...

    async def delete(self, brand: Brand) -> None: ...
