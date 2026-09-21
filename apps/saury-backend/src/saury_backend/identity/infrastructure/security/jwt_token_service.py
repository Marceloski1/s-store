from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from saury_backend.identity.application.ports.token_service import TokenClaims
from saury_backend.identity.domain.errors import NotAuthenticated
from saury_backend.identity.domain.value_objects.role import Role

_ALGORITHM = "HS256"


class JwtTokenService:
    def __init__(self, secret: str, expires_minutes: int) -> None:
        self._secret = secret
        self._expires = timedelta(minutes=expires_minutes)

    def issue(self, user_id: UUID, role: Role) -> str:
        now = datetime.now(UTC)
        claims = {"sub": str(user_id), "role": role.value, "iat": now, "exp": now + self._expires}
        return jwt.encode(claims, self._secret, algorithm=_ALGORITHM)

    def decode(self, token: str) -> TokenClaims:
        try:
            claims = jwt.decode(
                token, self._secret, algorithms=[_ALGORITHM], options={"require": ["sub", "role", "exp"]}
            )
            return TokenClaims(user_id=UUID(claims["sub"]), role=Role(claims["role"]))
        except (jwt.InvalidTokenError, ValueError) as error:
            raise NotAuthenticated() from error
