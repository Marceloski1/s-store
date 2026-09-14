from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

BACKEND_DIR = Path(__file__).resolve().parents[3]

_ASYNC_POSTGRES_DRIVER = "postgresql+asyncpg"
_POSTGRES_DRIVERS = {"postgres", "postgresql"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    database_url: str
    database_echo: bool = False

    @property
    def async_database_url(self) -> str:
        return to_async_database_url(self.database_url)


def to_async_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if url.drivername not in _POSTGRES_DRIVERS:
        return database_url
    query = dict(url.query)
    ssl_mode = query.pop("sslmode", None)
    query.pop("channel_binding", None)
    if ssl_mode is not None:
        query["ssl"] = ssl_mode
    return url.set(drivername=_ASYNC_POSTGRES_DRIVER, query=query).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
