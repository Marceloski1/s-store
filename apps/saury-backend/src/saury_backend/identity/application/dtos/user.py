from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID

from saury_backend.identity.domain.entities.user import User


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> Self:
        return cls(
            id=user.id,
            email=user.email.value,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@dataclass(frozen=True, slots=True)
class SessionDTO:
    user: UserDTO
    token: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class LoginCommand:
    email: str
    password: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    email: str
    name: str
    password: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class UpdateAdminUserCommand:
    user_id: UUID
    name: str | None = None
    is_active: bool | None = None
    password: str | None = field(default=None, repr=False)
