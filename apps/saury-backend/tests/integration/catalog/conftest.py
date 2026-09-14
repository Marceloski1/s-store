import asyncio
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from shared.infrastructure.persistence.database import Base, create_engine

from saury_backend.config.settings import Settings
from saury_backend.main import create_app


async def _create_schema(database_url: str) -> None:
    engine = create_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    database_url = f"sqlite+aiosqlite:///{(tmp_path / 'catalog.db').as_posix()}"
    asyncio.run(_create_schema(database_url))
    with TestClient(create_app(Settings(database_url=database_url))) as test_client:
        yield test_client
