from dataclasses import replace
from uuid import UUID

import pytest
from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.domain.entities.brand import Brand
from saury_backend.catalog.domain.entities.category import Category


class InMemoryRepository[E: (Brand, Category)]:
    def __init__(self) -> None:
        self._items: dict[UUID, E] = {}

    async def save(self, entity: E) -> None:
        self._items[entity.id] = replace(entity)

    async def get(self, entity_id: UUID) -> E | None:
        entity = self._items.get(entity_id)
        return replace(entity) if entity is not None else None

    async def get_by_slug(self, slug: Slug) -> E | None:
        return next((replace(entity) for entity in self._items.values() if entity.slug == slug), None)

    async def paginate(self, params: PageParams) -> Page[E]:
        ordered = sorted(self._items.values(), key=lambda entity: (entity.name, entity.id))
        return Page(
            items=[replace(entity) for entity in ordered[params.offset : params.offset + params.size]],
            total=len(ordered),
            page=params.page,
            size=params.size,
        )

    async def delete(self, entity: E) -> None:
        self._items.pop(entity.id, None)


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        pass


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def brand_repository() -> InMemoryRepository[Brand]:
    return InMemoryRepository[Brand]()


@pytest.fixture
def category_repository() -> InMemoryRepository[Category]:
    return InMemoryRepository[Category]()
