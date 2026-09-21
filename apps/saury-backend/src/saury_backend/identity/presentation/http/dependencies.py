from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import APIKeyCookie
from shared.presentation.http.dependencies import SessionDep

from saury_backend.config.settings import Settings
from saury_backend.identity.application.dtos.user import UserDTO
from saury_backend.identity.application.ports.password_hasher import PasswordHasher
from saury_backend.identity.application.ports.token_service import TokenService
from saury_backend.identity.application.use_cases.auth import Authenticate
from saury_backend.identity.domain.errors import InsufficientRole
from saury_backend.identity.domain.repositories.user_repository import UserRepository
from saury_backend.identity.domain.value_objects.role import Role
from saury_backend.identity.infrastructure.persistence.user_repository import SqlAlchemyUserRepository
from saury_backend.identity.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher
from saury_backend.identity.infrastructure.security.jwt_token_service import JwtTokenService

SESSION_COOKIE = "saury_session"

_session_cookie = APIKeyCookie(name=SESSION_COOKIE, auto_error=False)
_password_hasher = Argon2PasswordHasher()


def get_user_repository(session: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_password_hasher() -> PasswordHasher:
    return _password_hasher


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


AppSettingsDep = Annotated[Settings, Depends(get_app_settings)]


def get_token_service(settings: AppSettingsDep) -> TokenService:
    secret = settings.jwt_secret.get_secret_value() if settings.jwt_secret is not None else ""
    return JwtTokenService(secret=secret, expires_minutes=settings.jwt_expires_minutes)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


async def get_current_user(
    token: Annotated[str | None, Depends(_session_cookie)],
    repository: UserRepositoryDep,
    tokens: TokenServiceDep,
) -> UserDTO:
    return await Authenticate(repository, tokens).execute(token)


CurrentUserDep = Annotated[UserDTO, Depends(get_current_user)]


def require_role(role: Role) -> Callable[[UserDTO], Awaitable[UserDTO]]:
    async def dependency(user: CurrentUserDep) -> UserDTO:
        if user.role != role.value:
            raise InsufficientRole(role)
        return user

    return dependency


require_admin = require_role(Role.ADMIN)
require_super_admin = require_role(Role.SUPER_ADMIN)

AdminDep = Annotated[UserDTO, Depends(require_admin)]
SuperAdminDep = Annotated[UserDTO, Depends(require_super_admin)]
