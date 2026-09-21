import os
import secrets
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

BACKEND_DIR = Path(__file__).resolve().parents[3]

_ASYNC_POSTGRES_DRIVER = "postgresql+asyncpg"
_POSTGRES_DRIVERS = {"postgres", "postgresql"}


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_env: Environment = Environment.DEVELOPMENT
    database_url: str
    database_echo: bool = False
    cors_origins: list[str] = []
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: SecretStr | None = None
    cloudinary_folder: str = "sauri-store"
    jwt_secret: SecretStr | None = None
    jwt_expires_minutes: int = 480

    @model_validator(mode="after")
    def _ensure_jwt_secret(self) -> Settings:
        if self.jwt_secret is None:
            if self.app_env is Environment.PRODUCTION:
                raise ValueError("JWT_SECRET is required in production")
            self.jwt_secret = SecretStr(secrets.token_urlsafe(32))
        return self

    @property
    def cookie_secure(self) -> bool:
        return self.app_env is Environment.PRODUCTION

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


def env_files_for(app_env: Environment) -> tuple[Path, ...]:
    return (BACKEND_DIR / ".env", BACKEND_DIR / f".env.{app_env}")


@lru_cache
def get_settings() -> Settings:
    app_env = Environment(os.environ.get("APP_ENV", Environment.DEVELOPMENT))
    return Settings(_env_file=env_files_for(app_env))
