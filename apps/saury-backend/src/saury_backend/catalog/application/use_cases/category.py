from uuid import UUID

from shared.application.unit_of_work import UnitOfWork
from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.application.dtos.category import (
    CategoryDTO,
    CreateCategoryCommand,
    UpdateCategoryCommand,
)
from saury_backend.catalog.domain.entities.category import Category
from saury_backend.catalog.domain.errors import CategoryInUse, CategoryNotFound, CategorySlugAlreadyExists
from saury_backend.catalog.domain.repositories.category_repository import CategoryRepository
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerRepository


async def _get_category(repository: CategoryRepository, category_id: UUID) -> Category:
    category = await repository.get(category_id)
    if category is None:
        raise CategoryNotFound(category_id)
    return category


async def _ensure_slug_is_available(repository: CategoryRepository, category: Category) -> None:
    existing = await repository.get_by_slug(category.slug)
    if existing is not None and existing.id != category.id:
        raise CategorySlugAlreadyExists(category.slug)


class CreateCategory:
    def __init__(self, repository: CategoryRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, command: CreateCategoryCommand) -> CategoryDTO:
        category = Category.create(command.name, Slug(command.slug) if command.slug else None)
        await _ensure_slug_is_available(self._repository, category)
        await self._repository.save(category)
        await self._unit_of_work.commit()
        return CategoryDTO.from_entity(category)


class GetCategory:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    async def execute(self, category_id: UUID) -> CategoryDTO:
        return CategoryDTO.from_entity(await _get_category(self._repository, category_id))


class ListCategories:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    async def execute(self, params: PageParams) -> Page[CategoryDTO]:
        page = await self._repository.paginate(params)
        return page.map(CategoryDTO.from_entity)


class UpdateCategory:
    def __init__(self, repository: CategoryRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, command: UpdateCategoryCommand) -> CategoryDTO:
        category = await _get_category(self._repository, command.category_id)
        category.update(command.name, Slug(command.slug) if command.slug else None)
        await _ensure_slug_is_available(self._repository, category)
        await self._repository.save(category)
        await self._unit_of_work.commit()
        return CategoryDTO.from_entity(category)


class DeleteCategory:
    def __init__(
        self, repository: CategoryRepository, sneaker_repository: SneakerRepository, unit_of_work: UnitOfWork
    ) -> None:
        self._repository = repository
        self._sneaker_repository = sneaker_repository
        self._unit_of_work = unit_of_work

    async def execute(self, category_id: UUID) -> None:
        category = await _get_category(self._repository, category_id)
        if await self._sneaker_repository.exists_for_category(category.id):
            raise CategoryInUse(category.id)
        await self._repository.delete(category)
        await self._unit_of_work.commit()
