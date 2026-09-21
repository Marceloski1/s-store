from uuid import UUID

from fastapi import APIRouter, Depends, status
from shared.presentation.http.dependencies import PageParamsDep, UnitOfWorkDep
from shared.presentation.http.schemas import AUTH_RESPONSES, CONFLICT_RESPONSE, NOT_FOUND_RESPONSE, PageResponse

from saury_backend.catalog.application.dtos.category import CreateCategoryCommand, UpdateCategoryCommand
from saury_backend.catalog.application.use_cases.category import (
    CreateCategory,
    DeleteCategory,
    GetCategory,
    ListCategories,
    UpdateCategory,
)
from saury_backend.catalog.presentation.http.dependencies import CategoryRepositoryDep, SneakerRepositoryDep
from saury_backend.catalog.presentation.http.schemas import CategoryRequest, CategoryResponse
from saury_backend.identity.presentation.http.dependencies import require_admin

ADMIN_ONLY = [Depends(require_admin)]

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=AUTH_RESPONSES | CONFLICT_RESPONSE,
    dependencies=ADMIN_ONLY,
)
async def create_category(
    body: CategoryRequest,
    repository: CategoryRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> CategoryResponse:
    command = CreateCategoryCommand(name=body.name, slug=body.slug)
    return CategoryResponse.model_validate(await CreateCategory(repository, unit_of_work).execute(command))


@router.get("")
async def list_categories(
    repository: CategoryRepositoryDep,
    page_params: PageParamsDep,
) -> PageResponse[CategoryResponse]:
    page = await ListCategories(repository).execute(page_params)
    return PageResponse[CategoryResponse].from_page(page.map(CategoryResponse.model_validate))


@router.get("/{category_id}", responses=NOT_FOUND_RESPONSE)
async def get_category(category_id: UUID, repository: CategoryRepositoryDep) -> CategoryResponse:
    return CategoryResponse.model_validate(await GetCategory(repository).execute(category_id))


@router.put(
    "/{category_id}",
    responses=AUTH_RESPONSES | NOT_FOUND_RESPONSE | CONFLICT_RESPONSE,
    dependencies=ADMIN_ONLY,
)
async def update_category(
    category_id: UUID,
    body: CategoryRequest,
    repository: CategoryRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> CategoryResponse:
    command = UpdateCategoryCommand(category_id=category_id, name=body.name, slug=body.slug)
    return CategoryResponse.model_validate(await UpdateCategory(repository, unit_of_work).execute(command))


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=AUTH_RESPONSES | NOT_FOUND_RESPONSE | CONFLICT_RESPONSE,
    dependencies=ADMIN_ONLY,
)
async def delete_category(
    category_id: UUID,
    repository: CategoryRepositoryDep,
    sneaker_repository: SneakerRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> None:
    await DeleteCategory(repository, sneaker_repository, unit_of_work).execute(category_id)
