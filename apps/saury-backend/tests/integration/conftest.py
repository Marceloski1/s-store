import asyncio
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from shared.infrastructure.persistence.database import Base, create_engine

from saury_backend.catalog.presentation.http.dependencies import get_image_storage
from saury_backend.config.settings import Settings
from saury_backend.identity.domain.value_objects.role import Role
from saury_backend.main import create_app
from support.identity import ADMIN_EMAIL, SUPER_ADMIN_EMAIL, login, seed_user
from support.image_storage import InMemoryImageStorage


async def _create_schema(database_url: str) -> None:
    engine = create_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    url = f"sqlite+aiosqlite:///{(tmp_path / 'app.db').as_posix()}"
    asyncio.run(_create_schema(url))
    return url


@pytest.fixture
def image_storage() -> InMemoryImageStorage:
    return InMemoryImageStorage()


@pytest.fixture
def app(database_url: str, image_storage: InMemoryImageStorage) -> FastAPI:
    application = create_app(Settings(database_url=database_url, _env_file=None))
    application.dependency_overrides[get_image_storage] = lambda: image_storage
    return application


@pytest.fixture
def http_client(app: FastAPI, database_url: str) -> Iterator[TestClient]:
    asyncio.run(seed_user(database_url, ADMIN_EMAIL, Role.ADMIN))
    asyncio.run(seed_user(database_url, SUPER_ADMIN_EMAIL, Role.SUPER_ADMIN))
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client(http_client: TestClient) -> TestClient:
    login(http_client, ADMIN_EMAIL)
    return http_client
