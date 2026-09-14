from saury_backend.config.settings import to_async_database_url


def test_converts_neon_url_to_asyncpg_url() -> None:
    url = to_async_database_url(
        "postgresql://user:secret@ep-example-pooler.neon.tech/neondb?sslmode=require&channel_binding=require"
    )

    assert url == "postgresql+asyncpg://user:secret@ep-example-pooler.neon.tech/neondb?ssl=require"


def test_converts_postgres_scheme_without_query() -> None:
    assert to_async_database_url("postgres://user:secret@localhost/app") == "postgresql+asyncpg://user:secret@localhost/app"


def test_keeps_non_postgres_urls_untouched() -> None:
    assert to_async_database_url("sqlite+aiosqlite:///catalog.db") == "sqlite+aiosqlite:///catalog.db"
