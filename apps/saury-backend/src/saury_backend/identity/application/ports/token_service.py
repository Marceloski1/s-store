from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from saury_backend.identity.domain.value_objects.role import Role


@dataclass(frozen=True, slots=True)
class TokenClaims:
    user_id: UUID
    role: Role


class TokenService(Protocol):
    def issue(self, user_id: UUID, role: Role) -> str: ...

    def decode(self, token: str) -> TokenClaims: ...
