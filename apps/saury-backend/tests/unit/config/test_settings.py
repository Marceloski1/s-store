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


def test_jwt_secret_is_required_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(_env_file=None, database_url="sqlite+aiosqlite:///catalog.db", app_env="production")


def test_development_generates_an_ephemeral_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)

    first = Settings(_env_file=None, database_url="sqlite+aiosqlite:///catalog.db")
    second = Settings(_env_file=None, database_url="sqlite+aiosqlite:///catalog.db")

    assert first.jwt_secret is not None and second.jwt_secret is not None
    assert first.jwt_secret.get_secret_value() != second.jwt_secret.get_secret_value()
    assert (first.jwt_expires_minutes, first.cookie_secure) == (480, False)


def test_reads_jwt_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///catalog.db")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "production-secret-value")
    monkeypatch.setenv("JWT_EXPIRES_MINUTES", "60")

    settings = Settings(_env_file=None)

    assert settings.jwt_secret is not None
    assert settings.jwt_secret.get_secret_value() == "production-secret-value"
    assert "production-secret-value" not in repr(settings)
    assert (settings.jwt_expires_minutes, settings.cookie_secure) == (60, True)
