from fastapi import APIRouter, Response, status

from shared.presentation.http.dependencies import UnitOfWorkDep
from saury_backend.identity.application.dtos.user import LoginCommand
from saury_backend.identity.application.use_cases.auth import Login
from saury_backend.identity.presentation.http.dependencies import (
    SESSION_COOKIE,
    AppSettingsDep,
    CurrentUserDep,
    PasswordHasherDep,
    TokenServiceDep,
    UserRepositoryDep,
)
from saury_backend.identity.presentation.http.schemas import LoginRequest, UserResponse
from saury_backend.identity.presentation.http.schemas import ChangePasswordRequest
from saury_backend.identity.domain.errors import InvalidCredentials
from saury_backend.identity.domain.value_objects.password import validate_password
from saury_backend.presentation.http.errors import UNAUTHORIZED_RESPONSE

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", responses=UNAUTHORIZED_RESPONSE)
async def login(
    body: LoginRequest,
    response: Response,
    repository: UserRepositoryDep,
    hasher: PasswordHasherDep,
    tokens: TokenServiceDep,
    settings: AppSettingsDep,
) -> UserResponse:
    session = await Login(repository, hasher, tokens).execute(LoginCommand(email=body.email, password=body.password))
    response.set_cookie(
        SESSION_COOKIE,
        session.token,
        max_age=settings.jwt_expires_minutes * 60,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
    return UserResponse.model_validate(session.user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, settings: AppSettingsDep) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, secure=settings.cookie_secure, samesite="lax")


@router.get("/me", responses=UNAUTHORIZED_RESPONSE)
async def me(user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(user)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: ChangePasswordRequest,
    user: CurrentUserDep,
    repository: UserRepositoryDep,
    hasher: PasswordHasherDep,
    unit_of_work: UnitOfWorkDep,
) -> None:
    account = await repository.get(user.id)
    if account is None or not hasher.verify(account.password_hash, body.current_password):
        raise InvalidCredentials()
    account.change_password_hash(hasher.hash(validate_password(body.new_password)))
    await repository.save(account)
    await unit_of_work.commit()
