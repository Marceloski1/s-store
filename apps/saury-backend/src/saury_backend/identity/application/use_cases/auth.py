from shared.domain.errors import ValidationError

from saury_backend.identity.application.dtos.user import LoginCommand, SessionDTO, UserDTO
from saury_backend.identity.application.ports.password_hasher import PasswordHasher
from saury_backend.identity.application.ports.token_service import TokenService
from saury_backend.identity.domain.errors import InactiveUser, InvalidCredentials, NotAuthenticated
from saury_backend.identity.domain.repositories.user_repository import UserRepository
from saury_backend.identity.domain.value_objects.email import Email


class Login:
    def __init__(self, repository: UserRepository, hasher: PasswordHasher, tokens: TokenService) -> None:
        self._repository = repository
        self._hasher = hasher
        self._tokens = tokens

    async def execute(self, command: LoginCommand) -> SessionDTO:
        try:
            email = Email(command.email)
        except ValidationError as error:
            self._hasher.verify_dummy(command.password)
            raise InvalidCredentials() from error
        user = await self._repository.get_by_email(email)
        if user is None:
            self._hasher.verify_dummy(command.password)
            raise InvalidCredentials()
        if not self._hasher.verify(user.password_hash, command.password):
            raise InvalidCredentials()
        if not user.is_active:
            raise InactiveUser()
        return SessionDTO(user=UserDTO.from_entity(user), token=self._tokens.issue(user.id, user.role))


class Authenticate:
    def __init__(self, repository: UserRepository, tokens: TokenService) -> None:
        self._repository = repository
        self._tokens = tokens

    async def execute(self, token: str | None) -> UserDTO:
        if not token:
            raise NotAuthenticated()
        claims = self._tokens.decode(token)
        user = await self._repository.get(claims.user_id)
        if user is None:
            raise NotAuthenticated()
        if not user.is_active:
            raise InactiveUser()
        return UserDTO.from_entity(user)
