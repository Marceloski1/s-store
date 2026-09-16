import asyncio
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from shared.infrastructure.persistence.database import Base, create_engine

from saury_backend.catalog.presentation.http.dependencies import get_image_storage
from saury_backend.config.settings import Settings
from saury_backend.main import create_app
from support.image_storage import InMemoryImageStorage


async def _create_schema(database_url: str) -> None:
    engine = create_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture
def image_storage() -> InMemoryImageStorage:
    return InMemoryImageStorage()


@pytest.fixture
def app(tmp_path: Path, image_storage: InMemoryImageStorage) -> FastAPI:
    database_url = f"sqlite+aiosqlite:///{(tmp_path / 'catalog.db').as_posix()}"
    asyncio.run(_create_schema(database_url))
    application = create_app(Settings(database_url=database_url))
    application.dependency_overrides[get_image_storage] = lambda: image_storage
    return application


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
