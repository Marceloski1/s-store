from decimal import Decimal
from uuid import UUID

from shared.application.unit_of_work import UnitOfWork
from shared.domain.money import Money

from saury_backend.catalog.application.dtos.sneaker import (
    CreateColorwayCommand,
    SneakerDTO,
    UpdateColorwayCommand,
)
from saury_backend.catalog.application.use_cases.sneaker import get_sneaker
from saury_backend.catalog.domain.entities.colorway import normalize_sku
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.errors import SkuAlreadyExists
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerRepository


class _ColorwayUseCase:
    def __init__(self, repository: SneakerRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def _ensure_sku_is_available(self, sneaker: Sneaker, sku: str) -> None:
        normalized = normalize_sku(sku)
        owner = await self._repository.find_sku_owner(normalized)
        if owner is not None and owner != sneaker.id:
            raise SkuAlreadyExists(normalized)

    async def _persist(self, sneaker: Sneaker) -> SneakerDTO:
        await self._repository.save(sneaker)
        await self._unit_of_work.commit()
        return SneakerDTO.from_entity(sneaker)


def _override(sneaker: Sneaker, amount: Decimal | None) -> Money | None:
    if amount is None:
        return None
    return Money.of(amount, sneaker.base_price.currency)


class CreateColorway(_ColorwayUseCase):
    async def execute(self, command: CreateColorwayCommand) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, command.sneaker_id)
        await self._ensure_sku_is_available(sneaker, command.sku)
        sneaker.add_colorway(command.name, command.color_code, command.sku, _override(sneaker, command.price_override))
        return await self._persist(sneaker)


class UpdateColorway(_ColorwayUseCase):
    async def execute(self, command: UpdateColorwayCommand) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, command.sneaker_id)
        await self._ensure_sku_is_available(sneaker, command.sku)
        sneaker.update_colorway(
            command.colorway_id,
            command.name,
            command.color_code,
            command.sku,
            _override(sneaker, command.price_override),
        )
        return await self._persist(sneaker)


class DeleteColorway(_ColorwayUseCase):
    async def execute(self, sneaker_id: UUID, colorway_id: UUID) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, sneaker_id)
        sneaker.remove_colorway(colorway_id)
        return await self._persist(sneaker)
