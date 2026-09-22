from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends
from shared.presentation.http.dependencies import UnitOfWorkDep

from saury_backend.catalog.application.dtos.sneaker import (
    CreateColorwayCommand,
    RemoveSizeCommand,
    SetSizeStockCommand,
    UpdateColorwayCommand,
)
from saury_backend.catalog.application.use_cases.colorway import CreateColorway, DeleteColorway, UpdateColorway
from saury_backend.catalog.application.use_cases.size_variant import RemoveSize, SetSizeStock
from saury_backend.catalog.presentation.http.dependencies import SneakerRepositoryDep
from saury_backend.catalog.presentation.http.schemas import ColorwayRequest, SizeStockRequest, SneakerResponse
from saury_backend.identity.presentation.http.dependencies import require_admin
from saury_backend.presentation.http.errors import AUTH_RESPONSES, CONFLICT_RESPONSE, NOT_FOUND_RESPONSE

router = APIRouter(
    prefix="/sneakers/{sneaker_id}/colorways",
    tags=["colorways"],
    dependencies=[Depends(require_admin)],
    responses=AUTH_RESPONSES,
)


@router.post("", status_code=201, responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def create_colorway(
    sneaker_id: UUID,
    body: ColorwayRequest,
    repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    command = CreateColorwayCommand(
        sneaker_id=sneaker_id,
        name=body.name,
        color_code=body.color_code,
        sku=body.sku,
        price_override=body.price_override,
    )
    return SneakerResponse.model_validate(await CreateColorway(repository, unit_of_work).execute(command))


@router.put("/{colorway_id}", responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def update_colorway(
    sneaker_id: UUID,
    colorway_id: UUID,
    body: ColorwayRequest,
    repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    command = UpdateColorwayCommand(
        sneaker_id=sneaker_id,
        colorway_id=colorway_id,
        name=body.name,
        color_code=body.color_code,
        sku=body.sku,
        price_override=body.price_override,
    )
    return SneakerResponse.model_validate(await UpdateColorway(repository, unit_of_work).execute(command))


@router.delete("/{colorway_id}", responses=NOT_FOUND_RESPONSE)
async def delete_colorway(
    sneaker_id: UUID,
    colorway_id: UUID,
    repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    return SneakerResponse.model_validate(
        await DeleteColorway(repository, unit_of_work).execute(sneaker_id, colorway_id)
    )


@router.put("/{colorway_id}/sizes/{size}", responses=NOT_FOUND_RESPONSE)
async def set_size_stock(
    sneaker_id: UUID,
    colorway_id: UUID,
    size: Decimal,
    body: SizeStockRequest,
    repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    command = SetSizeStockCommand(sneaker_id=sneaker_id, colorway_id=colorway_id, size=size, stock=body.stock)
    return SneakerResponse.model_validate(await SetSizeStock(repository, unit_of_work).execute(command))


@router.delete("/{colorway_id}/sizes/{size}", responses=NOT_FOUND_RESPONSE)
async def remove_size(
    sneaker_id: UUID,
    colorway_id: UUID,
    size: Decimal,
    repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    command = RemoveSizeCommand(sneaker_id=sneaker_id, colorway_id=colorway_id, size=size)
    return SneakerResponse.model_validate(await RemoveSize(repository, unit_of_work).execute(command))
