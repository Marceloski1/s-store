from dataclasses import replace
from uuid import UUID

from shared.domain.pagination import Page, PageParams

from saury_backend.identity.application.ports.token_service import TokenClaims
from saury_backend.identity.domain.entities.user import User
from saury_backend.identity.domain.errors import NotAuthenticated
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.role import Role


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, User] = {}

    async def save(self, user: User) -> None:
        self._items[user.id] = replace(user)

    async def get(self, user_id: UUID) -> User | None:
        user = self._items.get(user_id)
        return replace(user) if user is not None else None

    async def get_by_email(self, email: Email) -> User | None:
        return next((replace(user) for user in self._items.values() if user.email == email), None)

    async def paginate(self, params: PageParams) -> Page[User]:
        ordered = sorted(self._items.values(), key=lambda user: (user.name, user.id))
        return Page(
            items=[replace(user) for user in ordered[params.offset : params.offset + params.size]],
            total=len(ordered),
            page=params.page,
            size=params.size,
        )

    async def delete(self, user: User) -> None:
        self._items.pop(user.id, None)


class FakePasswordHasher:
    def __init__(self) -> None:
        self.dummy_verifications = 0

    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password_hash: str, password: str) -> bool:
        return password_hash == f"hashed:{password}"

    def verify_dummy(self, password: str) -> None:
        self.dummy_verifications += 1


class FakeTokenService:
    def issue(self, user_id: UUID, role: Role) -> str:
        return f"{user_id}|{role.value}"

    def decode(self, token: str) -> TokenClaims:
        try:
            user_id, role = token.split("|")
            return TokenClaims(user_id=UUID(user_id), role=Role(role))
        except ValueError as error:
            raise NotAuthenticated() from error


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        pass


async def store_user(
    repository: InMemoryUserRepository,
    email: str,
    role: Role = Role.ADMIN,
    *,
    password: str = "Password123!",
    is_active: bool = True,
) -> User:
    user = User.create(Email(email), email.split("@")[0], f"hashed:{password}", role)
    user.is_active = is_active
    await repository.save(user)
    return user
