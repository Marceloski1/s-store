from copy import deepcopy
from dataclasses import replace
from uuid import UUID

import pytest
from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.domain.entities.brand import Brand
from saury_backend.catalog.domain.entities.category import Category
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerFilters
from support.image_storage import InMemoryImageStorage


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


class InMemorySneakerRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Sneaker] = {}
        self.last_filters: SneakerFilters | None = None

    async def save(self, sneaker: Sneaker) -> None:
        self._items[sneaker.id] = deepcopy(sneaker)

    async def get(self, sneaker_id: UUID) -> Sneaker | None:
        sneaker = self._items.get(sneaker_id)
        return deepcopy(sneaker) if sneaker is not None else None

    async def get_by_slug(self, slug: Slug) -> Sneaker | None:
        return next((deepcopy(sneaker) for sneaker in self._items.values() if sneaker.slug == slug), None)

    async def find_sku_owner(self, sku: str) -> UUID | None:
        return next(
            (sneaker.id for sneaker in self._items.values() for colorway in sneaker.colorways if colorway.sku == sku),
            None,
        )

    async def paginate(self, filters: SneakerFilters, params: PageParams) -> Page[Sneaker]:
        self.last_filters = filters
        ordered = sorted(self._items.values(), key=lambda sneaker: sneaker.id)
        return Page(
            items=[deepcopy(sneaker) for sneaker in ordered[params.offset : params.offset + params.size]],
            total=len(ordered),
            page=params.page,
            size=params.size,
        )

    async def delete(self, sneaker: Sneaker) -> None:
        self._items.pop(sneaker.id, None)

    async def exists_for_brand(self, brand_id: UUID) -> bool:
        return any(sneaker.brand_id == brand_id for sneaker in self._items.values())

    async def exists_for_category(self, category_id: UUID) -> bool:
        return any(sneaker.category_id == category_id for sneaker in self._items.values())


class CommitFailed(Exception):
    pass


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.fail_on_commit = False

    async def commit(self) -> None:
        if self.fail_on_commit:
            raise CommitFailed("commit failed")
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


@pytest.fixture
def image_storage() -> InMemoryImageStorage:
    return InMemoryImageStorage()


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def brand_repository() -> InMemoryRepository[Brand]:
    return InMemoryRepository[Brand]()


@pytest.fixture
def category_repository() -> InMemoryRepository[Category]:
    return InMemoryRepository[Category]()


@pytest.fixture
def sneaker_repository() -> InMemorySneakerRepository:
    return InMemorySneakerRepository()


@pytest.fixture
async def brand(brand_repository: InMemoryRepository[Brand]) -> Brand:
    brand = Brand.create("Nike")
    await brand_repository.save(brand)
    return brand


@pytest.fixture
async def category(category_repository: InMemoryRepository[Category]) -> Category:
    category = Category.create("Running")
    await category_repository.save(category)
    return category
