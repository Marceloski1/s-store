from uuid import UUID

from shared.application.unit_of_work import UnitOfWork
from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.application.dtos.brand import BrandDTO, CreateBrandCommand, UpdateBrandCommand
from saury_backend.catalog.domain.entities.brand import Brand
from saury_backend.catalog.domain.errors import BrandNotFound, BrandSlugAlreadyExists
from saury_backend.catalog.domain.repositories.brand_repository import BrandRepository


async def _get_brand(repository: BrandRepository, brand_id: UUID) -> Brand:
    brand = await repository.get(brand_id)
    if brand is None:
        raise BrandNotFound(brand_id)
    return brand


async def _ensure_slug_is_available(repository: BrandRepository, brand: Brand) -> None:
    existing = await repository.get_by_slug(brand.slug)
    if existing is not None and existing.id != brand.id:
        raise BrandSlugAlreadyExists(brand.slug)


class CreateBrand:
    def __init__(self, repository: BrandRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, command: CreateBrandCommand) -> BrandDTO:
        brand = Brand.create(command.name, Slug(command.slug) if command.slug else None)
        await _ensure_slug_is_available(self._repository, brand)
        await self._repository.save(brand)
        await self._unit_of_work.commit()
        return BrandDTO.from_entity(brand)


class GetBrand:
    def __init__(self, repository: BrandRepository) -> None:
        self._repository = repository

    async def execute(self, brand_id: UUID) -> BrandDTO:
        return BrandDTO.from_entity(await _get_brand(self._repository, brand_id))


class ListBrands:
    def __init__(self, repository: BrandRepository) -> None:
        self._repository = repository

    async def execute(self, params: PageParams) -> Page[BrandDTO]:
        page = await self._repository.paginate(params)
        return page.map(BrandDTO.from_entity)


class UpdateBrand:
    def __init__(self, repository: BrandRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, command: UpdateBrandCommand) -> BrandDTO:
        brand = await _get_brand(self._repository, command.brand_id)
        brand.update(command.name, Slug(command.slug) if command.slug else None)
        await _ensure_slug_is_available(self._repository, brand)
        await self._repository.save(brand)
        await self._unit_of_work.commit()
        return BrandDTO.from_entity(brand)


class DeleteBrand:
    def __init__(self, repository: BrandRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, brand_id: UUID) -> None:
        brand = await _get_brand(self._repository, brand_id)
        await self._repository.delete(brand)
        await self._unit_of_work.commit()
