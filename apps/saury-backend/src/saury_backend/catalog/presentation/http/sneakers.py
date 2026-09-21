from dataclasses import replace
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from shared.presentation.http.dependencies import PageParamsDep, UnitOfWorkDep
from shared.presentation.http.schemas import (
    AUTH_RESPONSES,
    CONFLICT_RESPONSE,
    NOT_FOUND_RESPONSE,
    UNPROCESSABLE_RESPONSE,
    PageResponse,
)

from saury_backend.catalog.application.dtos.sneaker import (
    CreateSneakerCommand,
    ListSneakersQuery,
    SpecSheetDTO,
    TestimonialDTO,
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
    GetSneakerBySlug,
    ListSneakers,
    UpdateSneaker,
)
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus
from saury_backend.catalog.presentation.http.dependencies import (
    BrandRepositoryDep,
    CategoryRepositoryDep,
    ImageStorageDep,
    SneakerRepositoryDep,
)
from saury_backend.catalog.presentation.http.schemas import SneakerRequest, SneakerResponse
from saury_backend.catalog.presentation.http.sneaker_queries import list_sneakers_query
from saury_backend.identity.presentation.http.dependencies import require_admin

router = APIRouter(
    prefix="/sneakers",
    tags=["sneakers"],
    dependencies=[Depends(require_admin)],
    responses=AUTH_RESPONSES,
)


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
        currency=body.currency.value,
        release_date=body.release_date,
        slug=body.slug,
        reference=body.reference,
        specs=SpecSheetDTO(**body.specs.model_dump()),
        usage=body.usage,
        testimonial=_testimonial(body),
    )
    sneaker = await CreateSneaker(repository, brand_repository, category_repository, unit_of_work).execute(command)
    return SneakerResponse.model_validate(sneaker)


def _testimonial(body: SneakerRequest) -> TestimonialDTO | None:
    return TestimonialDTO(**body.testimonial.model_dump()) if body.testimonial else None


@router.get("", responses=UNPROCESSABLE_RESPONSE)
async def list_sneakers(
    repository: SneakerRepositoryDep,
    page_params: PageParamsDep,
    query: Annotated[ListSneakersQuery, Depends(list_sneakers_query)],
    sneaker_status: Annotated[SneakerStatus | None, Query(alias="status")] = None,
) -> PageResponse[SneakerResponse]:
    scoped = replace(query, status=sneaker_status.value if sneaker_status else None)
    page = await ListSneakers(repository).execute(scoped, page_params)
    return PageResponse[SneakerResponse].from_page(page.map(SneakerResponse.model_validate))


@router.get("/by-slug/{slug}", responses=NOT_FOUND_RESPONSE)
async def get_sneaker_by_slug(slug: str, repository: SneakerRepositoryDep) -> SneakerResponse:
    return SneakerResponse.model_validate(await GetSneakerBySlug(repository).execute(slug))


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
        currency=body.currency.value,
        release_date=body.release_date,
        slug=body.slug,
        reference=body.reference,
        specs=SpecSheetDTO(**body.specs.model_dump()),
        usage=body.usage,
        testimonial=_testimonial(body),
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
