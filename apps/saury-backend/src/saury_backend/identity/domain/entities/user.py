from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self
from uuid import UUID, uuid7

from shared.domain.validation import require_text

from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.role import Role

USER_NAME_MAX_LENGTH = 100


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class User:
    id: UUID
    email: Email
    name: str
    password_hash: str
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        self.name = require_text(self.name, field="name", max_length=USER_NAME_MAX_LENGTH)

    @classmethod
    def create(cls, email: Email, name: str, password_hash: str, role: Role) -> Self:
        now = _now()
        return cls(
            id=uuid7(),
            email=email,
            name=name,
            password_hash=password_hash,
            role=role,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def rename(self, name: str) -> None:
        self.name = require_text(name, field="name", max_length=USER_NAME_MAX_LENGTH)
        self._touch()

    def set_active(self, is_active: bool) -> None:
        self.is_active = is_active
        self._touch()

    def change_password_hash(self, password_hash: str) -> None:
        self.password_hash = password_hash
        self._touch()

    def _touch(self) -> None:
        self.updated_at = _now()
