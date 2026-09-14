from uuid import UUID

from fastapi import APIRouter, status
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
from saury_backend.catalog.presentation.http.dependencies import BrandRepositoryDep
from saury_backend.catalog.presentation.http.schemas import BrandRequest, BrandResponse

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("", status_code=status.HTTP_201_CREATED)
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


@router.get("/{brand_id}")
async def get_brand(brand_id: UUID, repository: BrandRepositoryDep) -> BrandResponse:
    return BrandResponse.model_validate(await GetBrand(repository).execute(brand_id))


@router.put("/{brand_id}")
async def update_brand(
    brand_id: UUID,
    body: BrandRequest,
    repository: BrandRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> BrandResponse:
    command = UpdateBrandCommand(brand_id=brand_id, name=body.name, slug=body.slug)
    return BrandResponse.model_validate(await UpdateBrand(repository, unit_of_work).execute(command))


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(brand_id: UUID, repository: BrandRepositoryDep, unit_of_work: UnitOfWorkDep) -> None:
    await DeleteBrand(repository, unit_of_work).execute(brand_id)
