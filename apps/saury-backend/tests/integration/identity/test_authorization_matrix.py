import re
from uuid import uuid7

import pytest
from fastapi.testclient import TestClient

from saury_backend.config.settings import Settings
from saury_backend.identity.presentation.http.dependencies import SESSION_COOKIE
from saury_backend.main import create_app
from support.identity import ADMIN_EMAIL, SUPER_ADMIN_EMAIL, login

PUBLIC_ROUTES = {
    ("GET", "/"),
    ("POST", "/auth/login"),
    ("POST", "/auth/logout"),
    ("GET", "/brands"),
    ("GET", "/brands/{brand_id}"),
    ("GET", "/categories"),
    ("GET", "/categories/{category_id}"),
    ("GET", "/catalog/sneakers"),
    ("GET", "/catalog/sneakers/{slug}"),
    ("GET", "/catalog/facets"),
}
SESSION_ROUTES = {("GET", "/auth/me")}
PATH_VALUES = {"slug": "air-max-90", "size": "42"}


def _routes() -> list[tuple[str, str]]:
    app = create_app(Settings(database_url="sqlite+aiosqlite:///:memory:", _env_file=None))
    return sorted((method.upper(), path) for path, operations in app.openapi()["paths"].items() for method in operations)


PROTECTED_ROUTES = [route for route in _routes() if route not in PUBLIC_ROUTES | SESSION_ROUTES]


def _url(path: str) -> str:
    return re.sub(r"\{(\w+)\}", lambda match: PATH_VALUES.get(match.group(1), str(uuid7())), path)


def _required_role(path: str) -> str:
    return "SUPER_ADMIN" if path.startswith("/users") else "ADMIN"


@pytest.fixture
def tokens(http_client: TestClient) -> dict[str, str]:
    issued = {}
    for role, email in (("ADMIN", ADMIN_EMAIL), ("SUPER_ADMIN", SUPER_ADMIN_EMAIL)):
        login(http_client, email)
        issued[role] = http_client.cookies[SESSION_COOKIE]
    http_client.cookies.clear()
    return issued


def test_every_route_is_classified() -> None:
    documented = set(_routes())

    assert PUBLIC_ROUTES <= documented
    assert SESSION_ROUTES <= documented
    assert all(path.startswith(("/users", "/sneakers", "/brands", "/categories")) for _, path in PROTECTED_ROUTES)
    assert ("GET", "/sneakers") in PROTECTED_ROUTES
    assert ("DELETE", "/users/{user_id}") in PROTECTED_ROUTES


@pytest.mark.parametrize(("method", "path"), PROTECTED_ROUTES, ids=[f"{m} {p}" for m, p in PROTECTED_ROUTES])
def test_protected_routes_require_the_right_role(
    http_client: TestClient, tokens: dict[str, str], method: str, path: str
) -> None:
    url = _url(path)

    anonymous = http_client.request(method, url)

    wrong_role = "ADMIN" if _required_role(path) == "SUPER_ADMIN" else "SUPER_ADMIN"
    http_client.cookies.set(SESSION_COOKIE, tokens[wrong_role])
    forbidden = http_client.request(method, url)

    assert anonymous.status_code == 401, anonymous.text
    assert forbidden.status_code == 403, forbidden.text


@pytest.mark.parametrize(("method", "path"), sorted(PUBLIC_ROUTES), ids=[f"{m} {p}" for m, p in sorted(PUBLIC_ROUTES)])
def test_public_routes_do_not_require_a_session(http_client: TestClient, method: str, path: str) -> None:
    response = http_client.request(method, _url(path), json={} if method == "POST" else None)

    assert response.status_code not in (401, 403)
