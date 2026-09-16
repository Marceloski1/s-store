from uuid import UUID

from shared.application.unit_of_work import UnitOfWork

from saury_backend.catalog.application.dtos.sneaker import SneakerDTO
from saury_backend.catalog.application.use_cases.sneaker import get_sneaker
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerRepository


class _ChangeSneakerStatus:
    def __init__(self, repository: SneakerRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, sneaker_id: UUID) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, sneaker_id)
        self._apply(sneaker)
        await self._repository.save(sneaker)
        await self._unit_of_work.commit()
        return SneakerDTO.from_entity(sneaker)

    def _apply(self, sneaker: Sneaker) -> None:
        raise NotImplementedError


class PublishSneaker(_ChangeSneakerStatus):
    def _apply(self, sneaker: Sneaker) -> None:
        sneaker.publish()


class ArchiveSneaker(_ChangeSneakerStatus):
    def _apply(self, sneaker: Sneaker) -> None:
        sneaker.archive()


class UnarchiveSneaker(_ChangeSneakerStatus):
    def _apply(self, sneaker: Sneaker) -> None:
        sneaker.unarchive()
