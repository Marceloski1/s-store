from typing import Protocol
from uuid import UUID

from shared.domain.pagination import Page, PageParams

from saury_backend.identity.domain.entities.user import User
from saury_backend.identity.domain.value_objects.email import Email


class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...

    async def get(self, user_id: UUID) -> User | None: ...

    async def get_by_email(self, email: Email) -> User | None: ...

    async def paginate(self, params: PageParams) -> Page[User]: ...

    async def delete(self, user: User) -> None: ...
