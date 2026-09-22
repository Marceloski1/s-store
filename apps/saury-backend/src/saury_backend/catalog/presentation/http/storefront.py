from dataclasses import replace
from typing import Annotated

from fastapi import APIRouter, Depends
from shared.presentation.http.dependencies import PageParamsDep
from shared.presentation.http.schemas import PageResponse

from saury_backend.catalog.application.dtos.sneaker import ListSneakersQuery
from saury_backend.catalog.application.use_cases.sneaker import GetCatalogFacets, GetSneakerBySlug, ListSneakers
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus
from saury_backend.catalog.presentation.http.dependencies import SneakerRepositoryDep
from saury_backend.catalog.presentation.http.schemas import CatalogFacetsResponse, SneakerResponse
from saury_backend.catalog.presentation.http.sneaker_queries import list_sneakers_query
from saury_backend.presentation.http.errors import NOT_FOUND_RESPONSE, UNPROCESSABLE_RESPONSE

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/sneakers", responses=UNPROCESSABLE_RESPONSE)
async def list_published_sneakers(
    repository: SneakerRepositoryDep,
    page_params: PageParamsDep,
    query: Annotated[ListSneakersQuery, Depends(list_sneakers_query)],
) -> PageResponse[SneakerResponse]:
    published = replace(query, status=SneakerStatus.ACTIVE.value)
    page = await ListSneakers(repository).execute(published, page_params)
    return PageResponse[SneakerResponse].from_page(page.map(SneakerResponse.model_validate))


@router.get("/sneakers/{slug}", responses=NOT_FOUND_RESPONSE)
async def get_published_sneaker(slug: str, repository: SneakerRepositoryDep) -> SneakerResponse:
    return SneakerResponse.model_validate(await GetSneakerBySlug(repository).execute(slug, published_only=True))


@router.get("/facets")
async def get_catalog_facets(repository: SneakerRepositoryDep) -> CatalogFacetsResponse:
    return CatalogFacetsResponse.model_validate(await GetCatalogFacets(repository).execute())
