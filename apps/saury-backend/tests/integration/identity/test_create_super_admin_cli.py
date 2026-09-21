import asyncio
import sys

import pytest
from shared.infrastructure.persistence.database import create_engine, create_session_factory

from saury_backend.config.settings import Settings
from saury_backend.identity.domain.entities.user import User
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.infrastructure.persistence.user_repository import SqlAlchemyUserRepository
from saury_backend.identity.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher
from saury_backend.identity.presentation import cli


async def _stored(database_url: str, email: str) -> User | None:
    engine = create_engine(database_url)
    async with create_session_factory(engine)() as session:
        user = await SqlAlchemyUserRepository(session).get_by_email(Email(email))
    await engine.dispose()
    return user


@pytest.fixture
def run_cli(monkeypatch: pytest.MonkeyPatch, database_url: str):
    monkeypatch.setattr(cli, "get_settings", lambda: Settings(database_url=database_url, _env_file=None))
    monkeypatch.setenv(cli.PASSWORD_ENV_VAR, "SuperAdmin123!")

    def run(*arguments: str) -> None:
        monkeypatch.setattr(sys, "argv", ["create-super-admin", *arguments])
        cli.main()

    return run


def test_creates_a_super_admin(run_cli, database_url: str, capsys: pytest.CaptureFixture[str]) -> None:
    run_cli("--email", "Owner@Alesa.local", "--name", "Owner")

    user = asyncio.run(_stored(database_url, "owner@alesa.local"))
    assert user is not None
    assert (user.name, user.role.value, user.is_active) == ("Owner", "SUPER_ADMIN", True)
    assert Argon2PasswordHasher().verify(user.password_hash, "SuperAdmin123!")
    assert "SUPER_ADMIN created: owner@alesa.local" in capsys.readouterr().out


def test_fails_when_the_email_exists(run_cli, capsys: pytest.CaptureFixture[str]) -> None:
    run_cli("--email", "owner@alesa.local", "--name", "Owner")

    with pytest.raises(SystemExit) as exit_info:
        run_cli("--email", "OWNER@alesa.local", "--name", "Owner")

    assert exit_info.value.code == 1
    assert "already registered" in capsys.readouterr().err


def test_rejects_weak_passwords(run_cli, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(cli.PASSWORD_ENV_VAR, "short")

    with pytest.raises(SystemExit) as exit_info:
        run_cli("--email", "owner@alesa.local", "--name", "Owner")

    assert exit_info.value.code == 1
