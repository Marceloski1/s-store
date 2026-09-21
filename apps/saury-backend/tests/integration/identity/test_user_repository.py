import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from shared.domain.errors import ConflictError
from shared.domain.pagination import PageParams
from shared.infrastructure.persistence.database import Base, create_engine, create_session_factory
from shared.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession

from saury_backend.config.settings import to_async_database_url
from saury_backend.identity.domain.entities.user import User
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.role import Role
from saury_backend.identity.infrastructure.persistence.user_repository import SqlAlchemyUserRepository


@pytest.fixture
async def session(tmp_path: Path) -> AsyncIterator[AsyncSession]:
    configured_url = os.environ.get("TEST_DATABASE_URL")
    database_url = (
        to_async_database_url(configured_url)
        if configured_url
        else f"sqlite+aiosqlite:///{(tmp_path / 'identity.db').as_posix()}"
    )
    engine = create_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    async with create_session_factory(engine)() as db_session:
        yield db_session
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def repository(session: AsyncSession) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def make_user(email: str, role: Role = Role.ADMIN, name: str | None = None) -> User:
    return User.create(Email(email), name or email.split("@")[0], "$argon2id$hash", role)


async def test_round_trips_users(repository, session) -> None:
    user = make_user("Admin@Alesa.local", Role.SUPER_ADMIN, "Super Admin")
    await repository.save(user)
    await session.commit()
    session.expunge_all()

    loaded = await repository.get(user.id)
    by_email = await repository.get_by_email(Email("ADMIN@alesa.local"))

    assert loaded == user
    assert by_email == user
    assert await repository.get_by_email(Email("ghost@alesa.local")) is None


async def test_updates_and_deletes_users(repository, session) -> None:
    user = make_user("admin@alesa.local")
    await repository.save(user)
    await session.commit()

    user.rename("Eduardo")
    user.set_active(False)
    await repository.save(user)
    await session.commit()
    session.expunge_all()
    loaded = await repository.get(user.id)
    assert loaded is not None and (loaded.name, loaded.is_active) == ("Eduardo", False)

    await repository.delete(user)
    await session.commit()
    assert await repository.get(user.id) is None


async def test_paginates_users_by_name(repository, session) -> None:
    for name in ("Carla", "Ana", "Beto"):
        await repository.save(make_user(f"{name.lower()}@alesa.local", name=name))
    await session.commit()

    page = await repository.paginate(PageParams(page=2, size=2))

    assert ([user.name for user in page.items], page.total, page.pages) == (["Carla"], 3, 2)


async def test_emails_are_unique(repository, session) -> None:
    await repository.save(make_user("admin@alesa.local"))
    await session.commit()
    await repository.save(make_user("admin@alesa.local"))

    with pytest.raises(ConflictError):
        await SqlAlchemyUnitOfWork(session).commit()
