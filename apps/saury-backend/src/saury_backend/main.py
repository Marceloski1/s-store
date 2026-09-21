from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from shared.infrastructure.persistence.database import create_engine, create_session_factory
from shared.presentation.http.errors import register_error_handlers

from saury_backend.catalog.presentation.http.router import router as catalog_router
from saury_backend.config.settings import Settings, get_settings
from saury_backend.identity.presentation.http.router import router as identity_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_engine(resolved_settings.async_database_url, echo=resolved_settings.database_echo)
        app.state.session_factory = create_session_factory(engine)
        yield
        await engine.dispose()

    app = FastAPI(title="Saury Backend", lifespan=lifespan)
    app.state.settings = resolved_settings
    # TODO(cors): restrict allowed methods and headers before production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(identity_router)
    app.include_router(catalog_router)

    @app.get("/", response_class=PlainTextResponse)
    def hello() -> str:
        return "Hello world"

    return app


def main() -> None:
    uvicorn.run("saury_backend.main:create_app", factory=True, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
