from fastapi.testclient import TestClient

from saury_backend.config.settings import Settings
from saury_backend.main import create_app

ALLOWED_ORIGIN = "http://localhost:4321"


def _client() -> TestClient:
    settings = Settings(database_url="sqlite+aiosqlite:///:memory:", cors_origins=[ALLOWED_ORIGIN])
    return TestClient(create_app(settings))


def test_preflight_from_allowed_origin_is_accepted() -> None:
    response = _client().options(
        "/brands",
        headers={"Origin": ALLOWED_ORIGIN, "Access-Control-Request-Method": "POST"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


def test_preflight_from_unknown_origin_is_rejected() -> None:
    response = _client().options(
        "/brands",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"},
    )

    assert "access-control-allow-origin" not in response.headers
