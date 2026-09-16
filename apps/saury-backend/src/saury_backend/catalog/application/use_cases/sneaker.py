import logging
from uuid import UUID

from shared.application.unit_of_work import UnitOfWork
from shared.domain.errors import ValidationError
from shared.domain.money import Money
from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug

from saury_backend.catalog.application.dtos.sneaker import (
    CreateSneakerCommand,
    ListSneakersQuery,
    SneakerDTO,
    UpdateSneakerCommand,
)
from saury_backend.catalog.application.ports.image_storage import ImageStorage, ImageStorageError
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.errors import (
    BrandNotFound,
    CategoryNotFound,
    SneakerNotFound,
    SneakerSlugAlreadyExists,
)
from saury_backend.catalog.domain.repositories.brand_repository import BrandRepository
from saury_backend.catalog.domain.repositories.category_repository import CategoryRepository
from saury_backend.catalog.domain.repositories.sneaker_repository import (
    SneakerFilters,
    SneakerRepository,
    SneakerSort,
)
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus

logger = logging.getLogger(__name__)


async def get_sneaker(repository: SneakerRepository, sneaker_id: UUID) -> Sneaker:
    sneaker = await repository.get(sneaker_id)
    if sneaker is None:
        raise SneakerNotFound(sneaker_id)
    return sneaker


async def delete_stored_images(storage: ImageStorage, public_ids: list[str]) -> None:
    for public_id in public_ids:
        try:
            await storage.delete(public_id)
        except ImageStorageError:
            logger.exception("Failed to delete stored image %s", public_id)


def parse_enum[E: (Gender, SneakerStatus, SneakerSort)](enum: type[E], value: str, *, field: str) -> E:
    try:
        return enum(value)
    except ValueError as error:
        allowed = ", ".join(member.value for member in enum)
        raise ValidationError(f"{field} must be one of: {allowed}") from error


class _SneakerWriter:
    def __init__(
        self,
        repository: SneakerRepository,
        brand_repository: BrandRepository,
        category_repository: CategoryRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._brand_repository = brand_repository
        self._category_repository = category_repository
        self._unit_of_work = unit_of_work

    async def _ensure_references_exist(self, brand_id: UUID, category_id: UUID) -> None:
        if await self._brand_repository.get(brand_id) is None:
            raise BrandNotFound(brand_id)
        if await self._category_repository.get(category_id) is None:
            raise CategoryNotFound(category_id)

    async def _ensure_slug_is_available(self, sneaker: Sneaker) -> None:
        existing = await self._repository.get_by_slug(sneaker.slug)
        if existing is not None and existing.id != sneaker.id:
            raise SneakerSlugAlreadyExists(sneaker.slug)

    async def _persist(self, sneaker: Sneaker) -> SneakerDTO:
        await self._ensure_slug_is_available(sneaker)
        await self._repository.save(sneaker)
        await self._unit_of_work.commit()
        return SneakerDTO.from_entity(sneaker)


class CreateSneaker(_SneakerWriter):
    async def execute(self, command: CreateSneakerCommand) -> SneakerDTO:
        sneaker = Sneaker.create(
            name=command.name,
            description=command.description,
            brand_id=command.brand_id,
            category_id=command.category_id,
            gender=parse_enum(Gender, command.gender, field="gender"),
            base_price=Money.of(command.price, command.currency),
            release_date=command.release_date,
            slug=Slug(command.slug) if command.slug else None,
        )
        await self._ensure_references_exist(sneaker.brand_id, sneaker.category_id)
        return await self._persist(sneaker)


class UpdateSneaker(_SneakerWriter):
    async def execute(self, command: UpdateSneakerCommand) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, command.sneaker_id)
        sneaker.update(
            name=command.name,
            description=command.description,
            brand_id=command.brand_id,
            category_id=command.category_id,
            gender=parse_enum(Gender, command.gender, field="gender"),
            base_price=Money.of(command.price, command.currency),
            release_date=command.release_date,
            slug=Slug(command.slug) if command.slug else None,
        )
        await self._ensure_references_exist(sneaker.brand_id, sneaker.category_id)
        return await self._persist(sneaker)


class GetSneaker:
    def __init__(self, repository: SneakerRepository) -> None:
        self._repository = repository

    async def execute(self, sneaker_id: UUID) -> SneakerDTO:
        return SneakerDTO.from_entity(await get_sneaker(self._repository, sneaker_id))


class ListSneakers:
    def __init__(self, repository: SneakerRepository) -> None:
        self._repository = repository

    async def execute(self, query: ListSneakersQuery, params: PageParams) -> Page[SneakerDTO]:
        page = await self._repository.paginate(self._build_filters(query), params)
        return page.map(SneakerDTO.from_entity)

    @staticmethod
    def _build_filters(query: ListSneakersQuery) -> SneakerFilters:
        currency = query.currency
        if currency is None and (query.min_price is not None or query.max_price is not None):
            raise ValidationError("currency is required when filtering by price")
        return SneakerFilters(
            brand=Slug(query.brand) if query.brand else None,
            category=Slug(query.category) if query.category else None,
            gender=parse_enum(Gender, query.gender, field="gender") if query.gender else None,
            status=parse_enum(SneakerStatus, query.status, field="status") if query.status else None,
            size=ShoeSize.of(query.size) if query.size is not None else None,
            min_price=Money.of(query.min_price, currency) if query.min_price is not None and currency else None,
            max_price=Money.of(query.max_price, currency) if query.max_price is not None and currency else None,
            in_stock=query.in_stock,
            q=query.q,
            sort=parse_enum(SneakerSort, query.sort, field="sort"),
            descending=query.descending,
        )


class DeleteSneaker:
    def __init__(self, repository: SneakerRepository, image_storage: ImageStorage, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._image_storage = image_storage
        self._unit_of_work = unit_of_work

    async def execute(self, sneaker_id: UUID) -> None:
        sneaker = await get_sneaker(self._repository, sneaker_id)
        public_ids = [image.public_id for image in sneaker.images]
        await self._repository.delete(sneaker)
        await self._unit_of_work.commit()
        await delete_stored_images(self._image_storage, public_ids)
