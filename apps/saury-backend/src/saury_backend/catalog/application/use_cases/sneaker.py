import logging
import re
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
from saury_backend.catalog.domain.entities.colorway import COLOR_CODE_PATTERN
from saury_backend.catalog.domain.error_codes import CatalogErrorCode
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.errors import (
    BrandNotFound,
    CategoryNotFound,
    SneakerNotFound,
    SneakerReferenceAlreadyExists,
    SneakerSlugAlreadyExists,
    SneakerSlugNotFound,
)
from saury_backend.catalog.domain.repositories.brand_repository import BrandRepository
from saury_backend.catalog.domain.repositories.category_repository import CategoryRepository
from saury_backend.catalog.domain.repositories.sneaker_repository import (
    CatalogFacets,
    SneakerFilters,
    SneakerRepository,
    SneakerSort,
)
from saury_backend.catalog.domain.value_objects.currency import Currency
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus

logger = logging.getLogger(__name__)

_COLOR_CODE_REGEX = re.compile(COLOR_CODE_PATTERN)


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


def parse_enum[E: (Currency, Gender, SneakerStatus, SneakerSort)](enum: type[E], value: str, *, field: str) -> E:
    try:
        return enum(value)
    except ValueError as error:
        allowed = ", ".join(member.value for member in enum)
        raise ValidationError(
            f"{field} must be one of: {allowed}",
            code=CatalogErrorCode.INVALID_OPTION,
            params={"field": field, "value": value, "allowed": allowed},
        ) from error


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

    async def _ensure_reference_is_available(self, sneaker: Sneaker) -> None:
        if sneaker.reference is None:
            return
        owner = await self._repository.find_reference_owner(sneaker.reference)
        if owner is not None and owner != sneaker.id:
            raise SneakerReferenceAlreadyExists(sneaker.reference)

    async def _persist(self, sneaker: Sneaker) -> SneakerDTO:
        await self._ensure_slug_is_available(sneaker)
        await self._ensure_reference_is_available(sneaker)
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
            base_price=Money.of(command.price, parse_enum(Currency, command.currency, field="currency")),
            release_date=command.release_date,
            slug=Slug(command.slug) if command.slug else None,
            reference=command.reference,
            specs=command.specs.to_value(),
            usage=command.usage,
            testimonial=command.testimonial.to_value() if command.testimonial else None,
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
            base_price=Money.of(command.price, parse_enum(Currency, command.currency, field="currency")),
            release_date=command.release_date,
            slug=Slug(command.slug) if command.slug else None,
            reference=command.reference,
            specs=command.specs.to_value(),
            usage=command.usage,
            testimonial=command.testimonial.to_value() if command.testimonial else None,
        )
        await self._ensure_references_exist(sneaker.brand_id, sneaker.category_id)
        return await self._persist(sneaker)


class GetSneaker:
    def __init__(self, repository: SneakerRepository) -> None:
        self._repository = repository

    async def execute(self, sneaker_id: UUID) -> SneakerDTO:
        return SneakerDTO.from_entity(await get_sneaker(self._repository, sneaker_id))


class GetSneakerBySlug:
    def __init__(self, repository: SneakerRepository) -> None:
        self._repository = repository

    async def execute(self, slug: str, *, published_only: bool = False) -> SneakerDTO:
        value = Slug(slug)
        sneaker = await self._repository.get_by_slug(value)
        if sneaker is None or (published_only and sneaker.status is not SneakerStatus.ACTIVE):
            raise SneakerSlugNotFound(value)
        return SneakerDTO.from_entity(sneaker)


class GetCatalogFacets:
    def __init__(self, repository: SneakerRepository) -> None:
        self._repository = repository

    async def execute(self, *, published_only: bool = True) -> CatalogFacets:
        return await self._repository.facets(SneakerStatus.ACTIVE if published_only else None)


def _parse_color(value: str) -> str:
    color = value.strip().upper()
    if not _COLOR_CODE_REGEX.fullmatch(color):
        raise ValidationError(
            f"Invalid color code: '{value}'", code=CatalogErrorCode.INVALID_COLOR_CODE, params={"value": value}
        )
    return color


class ListSneakers:
    def __init__(self, repository: SneakerRepository) -> None:
        self._repository = repository

    async def execute(self, query: ListSneakersQuery, params: PageParams) -> Page[SneakerDTO]:
        page = await self._repository.paginate(self._build_filters(query), params)
        return page.map(SneakerDTO.from_entity)

    @staticmethod
    def _build_filters(query: ListSneakersQuery) -> SneakerFilters:
        currency = parse_enum(Currency, query.currency, field="currency") if query.currency else None
        if currency is None and (query.min_price is not None or query.max_price is not None):
            raise ValidationError(
                "currency is required when filtering by price", code=CatalogErrorCode.CURRENCY_REQUIRED
            )
        return SneakerFilters(
            brands=tuple(Slug(brand) for brand in query.brands),
            categories=tuple(Slug(category) for category in query.categories),
            genders=tuple(parse_enum(Gender, gender, field="gender") for gender in query.genders),
            status=parse_enum(SneakerStatus, query.status, field="status") if query.status else None,
            sizes=tuple(ShoeSize.of(size) for size in query.sizes),
            colors=tuple(_parse_color(color) for color in query.colors),
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
