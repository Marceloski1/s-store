from dataclasses import replace
from uuid import UUID, uuid7

import pytest
from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.application.ports.image_storage import StoredImage
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


class ImageStorageError(Exception):
    pass


class InMemoryImageStorage:
    def __init__(self) -> None:
        self.images: dict[str, bytes] = {}
        self.uploaded: list[StoredImage] = []
        self.deleted: list[str] = []
        self.fail_on_upload = False
        self.fail_on_delete = False

    async def upload(self, content: bytes, filename: str, folder: str) -> StoredImage:
        if self.fail_on_upload:
            raise ImageStorageError(f"upload failed for {filename}")
        public_id = f"{folder}/{uuid7().hex}"
        image = StoredImage(public_id=public_id, url=f"https://images.test/{public_id}")
        self.images[public_id] = content
        self.uploaded.append(image)
        return image

    async def delete(self, public_id: str) -> None:
        if self.fail_on_delete:
            raise ImageStorageError(f"delete failed for {public_id}")
        self.images.pop(public_id, None)
        self.deleted.append(public_id)


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
