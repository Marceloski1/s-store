from uuid import uuid7

import pytest

from saury_backend.identity.application.dtos.user import LoginCommand
from saury_backend.identity.application.use_cases.auth import Authenticate, Login
from saury_backend.identity.domain.errors import InactiveUser, InvalidCredentials, NotAuthenticated
from saury_backend.identity.domain.value_objects.role import Role
from support.identity_fakes import store_user


async def test_login_returns_the_user_and_a_token(user_repository, hasher, tokens) -> None:
    user = await store_user(user_repository, "admin@alesa.local")

    session = await Login(user_repository, hasher, tokens).execute(LoginCommand(" ADMIN@alesa.local ", "Password123!"))

    assert session.user.id == user.id
    assert session.user.role == "ADMIN"
    assert tokens.decode(session.token).user_id == user.id


@pytest.mark.parametrize(
    ("email", "password"),
    [("admin@alesa.local", "wrong-password"), ("missing@alesa.local", "Password123!"), ("not-an-email", "x")],
    ids=["wrong-password", "unknown-email", "invalid-email"],
)
async def test_login_rejects_invalid_credentials(user_repository, hasher, tokens, email, password) -> None:
    await store_user(user_repository, "admin@alesa.local")

    with pytest.raises(InvalidCredentials):
        await Login(user_repository, hasher, tokens).execute(LoginCommand(email, password))


@pytest.mark.parametrize("email", ["missing@alesa.local", "not-an-email"], ids=["unknown-email", "invalid-email"])
async def test_login_hashes_even_without_a_matching_user(user_repository, hasher, tokens, email) -> None:
    with pytest.raises(InvalidCredentials):
        await Login(user_repository, hasher, tokens).execute(LoginCommand(email, "Password123!"))

    assert hasher.dummy_verifications == 1


async def test_login_rejects_inactive_users(user_repository, hasher, tokens) -> None:
    await store_user(user_repository, "admin@alesa.local", is_active=False)

    with pytest.raises(InactiveUser):
        await Login(user_repository, hasher, tokens).execute(LoginCommand("admin@alesa.local", "Password123!"))


async def test_authenticate_loads_the_current_user(user_repository, tokens) -> None:
    user = await store_user(user_repository, "super@alesa.local", Role.SUPER_ADMIN)

    current = await Authenticate(user_repository, tokens).execute(tokens.issue(user.id, user.role))

    assert (current.id, current.role) == (user.id, "SUPER_ADMIN")


@pytest.mark.parametrize("token", [None, "", "garbage", f"{uuid7()}|ADMIN"], ids=["none", "empty", "invalid", "unknown"])
async def test_authenticate_rejects_missing_or_unknown_sessions(user_repository, tokens, token) -> None:
    with pytest.raises(NotAuthenticated):
        await Authenticate(user_repository, tokens).execute(token)


async def test_authenticate_rejects_inactive_users(user_repository, tokens) -> None:
    user = await store_user(user_repository, "admin@alesa.local", is_active=False)

    with pytest.raises(InactiveUser):
        await Authenticate(user_repository, tokens).execute(tokens.issue(user.id, user.role))
