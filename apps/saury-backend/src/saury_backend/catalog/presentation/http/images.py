from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, status
from shared.presentation.http.dependencies import UnitOfWorkDep

from saury_backend.catalog.application.dtos.sneaker import (
    ReorderSneakerImagesCommand,
    UploadSneakerImageCommand,
)
from saury_backend.catalog.application.use_cases.image import (
    DeleteSneakerImage,
    MarkPrimarySneakerImage,
    ReorderSneakerImages,
    UploadSneakerImage,
)
from saury_backend.catalog.presentation.http.dependencies import (
    ImageFolderDep,
    ImageStorageDep,
    SneakerRepositoryDep,
)
from saury_backend.catalog.presentation.http.image_upload import ImageUploadDep
from saury_backend.catalog.presentation.http.schemas import AltStr, ImageOrderRequest, SneakerResponse
from saury_backend.identity.presentation.http.dependencies import require_admin
from saury_backend.presentation.http.errors import (
    AUTH_RESPONSES,
    BAD_GATEWAY_RESPONSE,
    CONFLICT_RESPONSE,
    NOT_FOUND_RESPONSE,
    UNPROCESSABLE_RESPONSE,
)

router = APIRouter(
    prefix="/sneakers/{sneaker_id}/images",
    tags=["sneaker-images"],
    dependencies=[Depends(require_admin)],
    responses=AUTH_RESPONSES,
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE | UNPROCESSABLE_RESPONSE | BAD_GATEWAY_RESPONSE,
)
async def upload_sneaker_image(
    sneaker_id: UUID,
    image: ImageUploadDep,
    repository: SneakerRepositoryDep,
    image_storage: ImageStorageDep,
    folder: ImageFolderDep,
    unit_of_work: UnitOfWorkDep,
    alt: Annotated[AltStr, Form()] = "",
) -> SneakerResponse:
    command = UploadSneakerImageCommand(
        sneaker_id=sneaker_id, content=image.content, filename=image.filename, alt=alt
    )
    upload = UploadSneakerImage(repository, image_storage, unit_of_work, folder)
    return SneakerResponse.model_validate(await upload.execute(command))


@router.put("/order", responses=NOT_FOUND_RESPONSE | UNPROCESSABLE_RESPONSE)
async def reorder_sneaker_images(
    sneaker_id: UUID,
    body: ImageOrderRequest,
    repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    command = ReorderSneakerImagesCommand(sneaker_id=sneaker_id, image_ids=body.image_ids)
    return SneakerResponse.model_validate(await ReorderSneakerImages(repository, unit_of_work).execute(command))


@router.post("/{image_id}/primary", responses=NOT_FOUND_RESPONSE)
async def mark_primary_sneaker_image(
    sneaker_id: UUID,
    image_id: UUID,
    repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    marked = await MarkPrimarySneakerImage(repository, unit_of_work).execute(sneaker_id, image_id)
    return SneakerResponse.model_validate(marked)


@router.delete("/{image_id}", responses=NOT_FOUND_RESPONSE)
async def delete_sneaker_image(
    sneaker_id: UUID,
    image_id: UUID,
    repository: SneakerRepositoryDep,
    image_storage: ImageStorageDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    deleted = await DeleteSneakerImage(repository, image_storage, unit_of_work).execute(sneaker_id, image_id)
    return SneakerResponse.model_validate(deleted)
