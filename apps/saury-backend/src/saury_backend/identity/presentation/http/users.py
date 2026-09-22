from uuid import UUID

from fastapi import APIRouter, Depends, status
from shared.presentation.http.dependencies import PageParamsDep, UnitOfWorkDep
from shared.presentation.http.schemas import PageResponse

from saury_backend.identity.application.dtos.user import CreateUserCommand, UpdateAdminUserCommand
from saury_backend.identity.application.use_cases.user import (
    CreateAdminUser,
    DeleteAdminUser,
    ListUsers,
    UpdateAdminUser,
)
from saury_backend.identity.presentation.http.dependencies import (
    PasswordHasherDep,
    SuperAdminDep,
    UserRepositoryDep,
    require_super_admin,
)
from saury_backend.identity.presentation.http.schemas import CreateUserRequest, UpdateUserRequest, UserResponse
from saury_backend.presentation.http.errors import AUTH_RESPONSES, CONFLICT_RESPONSE, NOT_FOUND_RESPONSE

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_super_admin)],
    responses=AUTH_RESPONSES,
)


@router.get("")
async def list_users(repository: UserRepositoryDep, page_params: PageParamsDep) -> PageResponse[UserResponse]:
    page = await ListUsers(repository).execute(page_params)
    return PageResponse[UserResponse].from_page(page.map(UserResponse.model_validate))


@router.post("", status_code=status.HTTP_201_CREATED, responses=CONFLICT_RESPONSE)
async def create_user(
    body: CreateUserRequest,
    repository: UserRepositoryDep,
    hasher: PasswordHasherDep,
    unit_of_work: UnitOfWorkDep,
) -> UserResponse:
    command = CreateUserCommand(email=body.email, name=body.name, password=body.password)
    return UserResponse.model_validate(await CreateAdminUser(repository, hasher, unit_of_work).execute(command))


@router.patch("/{user_id}", responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def update_user(
    user_id: UUID,
    body: UpdateUserRequest,
    repository: UserRepositoryDep,
    hasher: PasswordHasherDep,
    unit_of_work: UnitOfWorkDep,
) -> UserResponse:
    command = UpdateAdminUserCommand(user_id=user_id, name=body.name, is_active=body.is_active, password=body.password)
    return UserResponse.model_validate(await UpdateAdminUser(repository, hasher, unit_of_work).execute(command))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND_RESPONSE | CONFLICT_RESPONSE)
async def delete_user(
    user_id: UUID,
    acting_user: SuperAdminDep,
    repository: UserRepositoryDep,
    unit_of_work: UnitOfWorkDep,
) -> None:
    await DeleteAdminUser(repository, unit_of_work).execute(user_id, acting_user.id)
