from shared.application.unit_of_work import UnitOfWork

from saury_backend.catalog.application.dtos.sneaker import RemoveSizeCommand, SetSizeStockCommand, SneakerDTO
from saury_backend.catalog.application.use_cases.sneaker import get_sneaker
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerRepository
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize


class SetSizeStock:
    def __init__(self, repository: SneakerRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, command: SetSizeStockCommand) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, command.sneaker_id)
        sneaker.set_size_stock(command.colorway_id, ShoeSize.of(command.size), command.stock)
        await self._repository.save(sneaker)
        await self._unit_of_work.commit()
        return SneakerDTO.from_entity(sneaker)


class RemoveSize:
    def __init__(self, repository: SneakerRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, command: RemoveSizeCommand) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, command.sneaker_id)
        sneaker.remove_size(command.colorway_id, ShoeSize.of(command.size))
        await self._repository.save(sneaker)
        await self._unit_of_work.commit()
        return SneakerDTO.from_entity(sneaker)
