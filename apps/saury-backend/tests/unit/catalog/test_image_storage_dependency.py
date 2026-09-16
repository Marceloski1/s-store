from types import SimpleNamespace

import pytest
from fastapi import Request

from saury_backend.catalog.infrastructure.storage.cloudinary_image_storage import CloudinaryImageStorage
from saury_backend.catalog.presentation.http.dependencies import get_image_storage
from saury_backend.config.settings import Settings


def request_with(settings: Settings) -> Request:
    return Request({"type": "http", "app": SimpleNamespace(state=SimpleNamespace(settings=settings))})


def test_builds_cloudinary_storage_from_settings() -> None:
    settings = Settings(
        _env_file=None,
        database_url="sqlite+aiosqlite:///catalog.db",
        cloudinary_cloud_name="demo",
        cloudinary_api_key="key",
        cloudinary_api_secret="secret",
    )

    assert isinstance(get_image_storage(request_with(settings)), CloudinaryImageStorage)


def test_fails_when_cloudinary_is_not_configured() -> None:
    settings = Settings(_env_file=None, database_url="sqlite+aiosqlite:///catalog.db")

    with pytest.raises(ValueError):
        get_image_storage(request_with(settings))
