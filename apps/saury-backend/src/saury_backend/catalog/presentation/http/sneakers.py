from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status
from shared.presentation.http.dependencies import PageParamsDep, UnitOfWorkDep
from shared.presentation.http.schemas import (
    CONFLICT_RESPONSE,
    NOT_FOUND_RESPONSE,
    UNPROCESSABLE_RESPONSE,
    PageResponse,
)

from saury_backend.catalog.application.dtos.sneaker import (
    CreateSneakerCommand,
    ListSneakersQuery,
    UpdateSneakerCommand,
)
from saury_backend.catalog.application.use_cases.publication import (
    ArchiveSneaker,
    PublishSneaker,
    UnarchiveSneaker,
)
from saury_backend.catalog.application.use_cases.sneaker import (
    CreateSneaker,
    DeleteSneaker,
    GetSneaker,
    ListSneakers,
    UpdateSneaker,
)
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerSort
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus
from saury_backend.catalog.presentation.http.dependencies import (
    BrandRepositoryDep,
    CategoryRepositoryDep,
    ImageStorageDep,
    SneakerRepositoryDep,
)
from saury_backend.catalog.presentation.http.schemas import SneakerRequest, SneakerResponse

router = APIRouter(prefix="/sneakers", tags=["sneakers"])


@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def create_sneaker(
    body: SneakerRequest,
    repository: SneakerRepositoryDep,
    brand_repository: BrandRepositoryDep,
    category_repository: CategoryRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    command = CreateSneakerCommand(
        name=body.name,
        description=body.description,
        brand_id=body.brand_id,
        category_id=body.category_id,
        gender=body.gender.value,
        price=body.price,
        currency=body.currency,
        release_date=body.release_date,
        slug=body.slug,
    )
    sneaker = await CreateSneaker(repository, brand_repository, category_repository, unit_of_work).execute(command)
    return SneakerResponse.model_validate(sneaker)


@router.get("", responses=UNPROCESSABLE_RESPONSE)
async def list_sneakers(
    repository: SneakerRepositoryDep,
    page_params: PageParamsDep,
    brand: str | None = None,
    category: str | None = None,
    gender: Gender | None = None,
    sneaker_status: Annotated[SneakerStatus | None, Query(alias="status")] = None,
    shoe_size: Decimal | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    currency: str | None = None,
    in_stock: bool = False,
    q: str | None = None,
    sort: SneakerSort = SneakerSort.CREATED_AT,
    descending: bool = False,
) -> PageResponse[SneakerResponse]:
    query = ListSneakersQuery(
        brand=brand,
        category=category,
        gender=gender.value if gender else None,
        status=sneaker_status.value if sneaker_status else None,
        size=shoe_size,
        min_price=min_price,
        max_price=max_price,
        currency=currency,
        in_stock=in_stock,
        q=q,
        sort=sort.value,
        descending=descending,
    )
    page = await ListSneakers(repository).execute(query, page_params)
    return PageResponse[SneakerResponse].from_page(page.map(SneakerResponse.model_validate))


@router.get("/{sneaker_id}", responses=NOT_FOUND_RESPONSE)
async def get_sneaker(sneaker_id: UUID, repository: SneakerRepositoryDep) -> SneakerResponse:
    return SneakerResponse.model_validate(await GetSneaker(repository).execute(sneaker_id))


@router.put("/{sneaker_id}", responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def update_sneaker(
    sneaker_id: UUID,
    body: SneakerRequest,
    repository: SneakerRepositoryDep,
    brand_repository: BrandRepositoryDep,
    category_repository: CategoryRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> SneakerResponse:
    command = UpdateSneakerCommand(
        sneaker_id=sneaker_id,
        name=body.name,
        description=body.description,
        brand_id=body.brand_id,
        category_id=body.category_id,
        gender=body.gender.value,
        price=body.price,
        currency=body.currency,
        release_date=body.release_date,
        slug=body.slug,
    )
    sneaker = await UpdateSneaker(repository, brand_repository, category_repository, unit_of_work).execute(command)
    return SneakerResponse.model_validate(sneaker)


@router.delete("/{sneaker_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND_RESPONSE)
async def delete_sneaker(
    sneaker_id: UUID,
    repository: SneakerRepositoryDep,
    image_storage: ImageStorageDep,
    unit_of_work: UnitOfWorkDep,
) -> None:
    await DeleteSneaker(repository, image_storage, unit_of_work).execute(sneaker_id)


@router.post("/{sneaker_id}/publish", responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def publish_sneaker(
    sneaker_id: UUID, repository: SneakerRepositoryDep, unit_of_work: UnitOfWorkDep
) -> SneakerResponse:
    return SneakerResponse.model_validate(await PublishSneaker(repository, unit_of_work).execute(sneaker_id))


@router.post("/{sneaker_id}/archive", responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def archive_sneaker(
    sneaker_id: UUID, repository: SneakerRepositoryDep, unit_of_work: UnitOfWorkDep
) -> SneakerResponse:
    return SneakerResponse.model_validate(await ArchiveSneaker(repository, unit_of_work).execute(sneaker_id))


@router.post("/{sneaker_id}/unarchive", responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def unarchive_sneaker(
    sneaker_id: UUID, repository: SneakerRepositoryDep, unit_of_work: UnitOfWorkDep
) -> SneakerResponse:
    return SneakerResponse.model_validate(await UnarchiveSneaker(repository, unit_of_work).execute(sneaker_id))
