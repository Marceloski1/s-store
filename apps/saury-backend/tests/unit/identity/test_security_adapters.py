from uuid import uuid7

import jwt
import pytest

from saury_backend.identity.domain.errors import NotAuthenticated
from saury_backend.identity.domain.value_objects.role import Role
from saury_backend.identity.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher
from saury_backend.identity.infrastructure.security.jwt_token_service import JwtTokenService

SECRET = "test-secret-with-enough-length-for-hs256"


def test_argon2_hasher_verifies_only_the_original_password() -> None:
    hasher = Argon2PasswordHasher()
    password_hash = hasher.hash("Password123!")

    assert password_hash.startswith("$argon2id$")
    assert hasher.verify(password_hash, "Password123!")
    assert not hasher.verify(password_hash, "password123!")
    assert not hasher.verify("not-a-hash", "Password123!")


def test_jwt_round_trip() -> None:
    tokens = JwtTokenService(SECRET, expires_minutes=5)
    user_id = uuid7()

    claims = tokens.decode(tokens.issue(user_id, Role.SUPER_ADMIN))

    assert (claims.user_id, claims.role) == (user_id, Role.SUPER_ADMIN)


@pytest.mark.parametrize(
    "token",
    [
        "garbage",
        JwtTokenService("another-secret-with-enough-length-!!", expires_minutes=5).issue(uuid7(), Role.ADMIN),
        JwtTokenService(SECRET, expires_minutes=-1).issue(uuid7(), Role.ADMIN),
        jwt.encode({"sub": "not-a-uuid", "role": "ADMIN", "exp": 9999999999}, SECRET, algorithm="HS256"),
        jwt.encode({"sub": str(uuid7()), "role": "OWNER", "exp": 9999999999}, SECRET, algorithm="HS256"),
        jwt.encode({"sub": str(uuid7()), "role": "ADMIN"}, SECRET, algorithm="HS256"),
    ],
    ids=["garbage", "wrong-secret", "expired", "invalid-subject", "invalid-role", "without-expiration"],
)
def test_jwt_rejects_invalid_tokens(token: str) -> None:
    with pytest.raises(NotAuthenticated):
        JwtTokenService(SECRET, expires_minutes=5).decode(token)
