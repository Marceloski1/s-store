import pytest

from saury_backend.config.settings import Settings, to_async_database_url


def test_converts_neon_url_to_asyncpg_url() -> None:
    url = to_async_database_url(
        "postgresql://user:secret@ep-example-pooler.neon.tech/neondb?sslmode=require&channel_binding=require"
    )

    assert url == "postgresql+asyncpg://user:secret@ep-example-pooler.neon.tech/neondb?ssl=require"


def test_converts_postgres_scheme_without_query() -> None:
    assert to_async_database_url("postgres://user:secret@localhost/app") == "postgresql+asyncpg://user:secret@localhost/app"


def test_keeps_non_postgres_urls_untouched() -> None:
    assert to_async_database_url("sqlite+aiosqlite:///catalog.db") == "sqlite+aiosqlite:///catalog.db"


def test_reads_cloudinary_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///catalog.db")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "top-secret-value")
    monkeypatch.setenv("CLOUDINARY_FOLDER", "sauri-store/test")

    settings = Settings(_env_file=None)

    assert settings.cloudinary_cloud_name == "demo"
    assert settings.cloudinary_api_key == "key"
    assert settings.cloudinary_api_secret is not None
    assert settings.cloudinary_api_secret.get_secret_value() == "top-secret-value"
    assert "top-secret-value" not in repr(settings)
    assert settings.cloudinary_folder == "sauri-store/test"


def test_cloudinary_settings_are_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///catalog.db")
    for name in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET", "CLOUDINARY_FOLDER"):
        monkeypatch.delenv(name, raising=False)

    settings = Settings(_env_file=None)

    assert settings.cloudinary_cloud_name is None
    assert settings.cloudinary_api_secret is None
    assert settings.cloudinary_folder == "sauri-store"
