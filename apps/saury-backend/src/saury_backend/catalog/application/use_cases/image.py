from uuid import UUID

from shared.application.unit_of_work import UnitOfWork

from saury_backend.catalog.application.dtos.sneaker import (
    ReorderSneakerImagesCommand,
    SneakerDTO,
    UploadSneakerImageCommand,
)
from saury_backend.catalog.application.ports.image_storage import ImageStorage
from saury_backend.catalog.application.use_cases.sneaker import delete_stored_images, get_sneaker
from saury_backend.catalog.domain.entities.sneaker import MAX_IMAGES_PER_SNEAKER
from saury_backend.catalog.domain.errors import ImageLimitExceeded
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerRepository


class UploadSneakerImage:
    def __init__(
        self,
        repository: SneakerRepository,
        image_storage: ImageStorage,
        unit_of_work: UnitOfWork,
        folder: str,
    ) -> None:
        self._repository = repository
        self._image_storage = image_storage
        self._unit_of_work = unit_of_work
        self._folder = folder

    async def execute(self, command: UploadSneakerImageCommand) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, command.sneaker_id)
        if len(sneaker.images) >= MAX_IMAGES_PER_SNEAKER:
            raise ImageLimitExceeded(MAX_IMAGES_PER_SNEAKER)
        stored = await self._image_storage.upload(
            command.content, command.filename, f"{self._folder}/sneakers/{sneaker.id}"
        )
        try:
            sneaker.add_image(stored.public_id, stored.url, command.alt)
            await self._repository.save(sneaker)
            await self._unit_of_work.commit()
        except Exception:
            await self._unit_of_work.rollback()
            await delete_stored_images(self._image_storage, [stored.public_id])
            raise
        return SneakerDTO.from_entity(sneaker)


class ReorderSneakerImages:
    def __init__(self, repository: SneakerRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, command: ReorderSneakerImagesCommand) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, command.sneaker_id)
        sneaker.reorder_images(command.image_ids)
        await self._repository.save(sneaker)
        await self._unit_of_work.commit()
        return SneakerDTO.from_entity(sneaker)


class MarkPrimarySneakerImage:
    def __init__(self, repository: SneakerRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, sneaker_id: UUID, image_id: UUID) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, sneaker_id)
        sneaker.mark_primary_image(image_id)
        await self._repository.save(sneaker)
        await self._unit_of_work.commit()
        return SneakerDTO.from_entity(sneaker)


class DeleteSneakerImage:
    def __init__(self, repository: SneakerRepository, image_storage: ImageStorage, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._image_storage = image_storage
        self._unit_of_work = unit_of_work

    async def execute(self, sneaker_id: UUID, image_id: UUID) -> SneakerDTO:
        sneaker = await get_sneaker(self._repository, sneaker_id)
        removed = sneaker.remove_image(image_id)
        await self._repository.save(sneaker)
        await self._unit_of_work.commit()
        await delete_stored_images(self._image_storage, [removed.public_id])
        return SneakerDTO.from_entity(sneaker)
