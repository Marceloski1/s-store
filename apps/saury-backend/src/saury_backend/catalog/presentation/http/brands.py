from uuid import UUID

from fastapi import APIRouter, Depends, status
from shared.presentation.http.dependencies import PageParamsDep, UnitOfWorkDep
from shared.presentation.http.schemas import PageResponse

from saury_backend.catalog.application.dtos.brand import CreateBrandCommand, UpdateBrandCommand
from saury_backend.catalog.application.use_cases.brand import (
    CreateBrand,
    DeleteBrand,
    GetBrand,
    ListBrands,
    UpdateBrand,
)
from saury_backend.catalog.presentation.http.dependencies import BrandRepositoryDep, SneakerRepositoryDep
from saury_backend.catalog.presentation.http.schemas import BrandRequest, BrandResponse
from saury_backend.identity.presentation.http.dependencies import require_admin
from saury_backend.presentation.http.errors import AUTH_RESPONSES, CONFLICT_RESPONSE, NOT_FOUND_RESPONSE

ADMIN_ONLY = [Depends(require_admin)]

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=AUTH_RESPONSES | CONFLICT_RESPONSE,
    dependencies=ADMIN_ONLY,
)
async def create_brand(
    body: BrandRequest,
    repository: BrandRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> BrandResponse:
    brand = await CreateBrand(repository, unit_of_work).execute(CreateBrandCommand(name=body.name, slug=body.slug))
    return BrandResponse.model_validate(brand)


@router.get("")
async def list_brands(repository: BrandRepositoryDep, page_params: PageParamsDep) -> PageResponse[BrandResponse]:
    page = await ListBrands(repository).execute(page_params)
    return PageResponse[BrandResponse].from_page(page.map(BrandResponse.model_validate))


@router.get("/{brand_id}", responses=NOT_FOUND_RESPONSE)
async def get_brand(brand_id: UUID, repository: BrandRepositoryDep) -> BrandResponse:
    return BrandResponse.model_validate(await GetBrand(repository).execute(brand_id))


@router.put(
    "/{brand_id}",
    responses=AUTH_RESPONSES | NOT_FOUND_RESPONSE | CONFLICT_RESPONSE,
    dependencies=ADMIN_ONLY,
)
async def update_brand(
    brand_id: UUID,
    body: BrandRequest,
    repository: BrandRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> BrandResponse:
    command = UpdateBrandCommand(brand_id=brand_id, name=body.name, slug=body.slug)
    return BrandResponse.model_validate(await UpdateBrand(repository, unit_of_work).execute(command))


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=AUTH_RESPONSES | NOT_FOUND_RESPONSE | CONFLICT_RESPONSE,
    dependencies=ADMIN_ONLY,
)
async def delete_brand(
    brand_id: UUID,
    repository: BrandRepositoryDep,
    sneaker_repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> None:
    await DeleteBrand(repository, sneaker_repository, unit_of_work).execute(brand_id)
