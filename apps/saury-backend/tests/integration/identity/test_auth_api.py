import asyncio

from fastapi.testclient import TestClient

from saury_backend.identity.domain.value_objects.role import Role
from saury_backend.identity.presentation.http.dependencies import SESSION_COOKIE
from support.identity import ADMIN_EMAIL, PASSWORD, SUPER_ADMIN_EMAIL, login, seed_user


def test_login_sets_an_http_only_session_cookie(http_client: TestClient) -> None:
    response = http_client.post("/auth/login", json={"email": " Admin@Test.local ", "password": PASSWORD})

    assert response.status_code == 200
    assert response.json()["email"] == ADMIN_EMAIL
    assert response.json()["role"] == "ADMIN"
    assert "password_hash" not in response.json()
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE}=")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Path=/" in cookie
    assert "Max-Age=28800" in cookie
    assert "Secure" not in cookie


def test_me_returns_the_logged_in_user(http_client: TestClient) -> None:
    login(http_client, SUPER_ADMIN_EMAIL)

    response = http_client.get("/auth/me")

    assert response.status_code == 200
    assert (response.json()["email"], response.json()["role"]) == (SUPER_ADMIN_EMAIL, "SUPER_ADMIN")


def test_me_requires_a_session(http_client: TestClient) -> None:
    assert http_client.get("/auth/me").status_code == 401
    http_client.cookies.set(SESSION_COOKIE, "tampered")
    assert http_client.get("/auth/me").status_code == 401


def test_login_rejects_invalid_credentials(http_client: TestClient) -> None:
    wrong_password = http_client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong-password"})
    unknown = http_client.post("/auth/login", json={"email": "ghost@test.local", "password": PASSWORD})

    assert (wrong_password.status_code, unknown.status_code) == (401, 401)
    assert wrong_password.json() == unknown.json() == {"detail": "Invalid email or password"}
    assert "set-cookie" not in wrong_password.headers


def test_inactive_users_cannot_log_in(http_client: TestClient, database_url: str) -> None:
    asyncio.run(seed_user(database_url, "inactive@test.local", Role.ADMIN, is_active=False))

    response = http_client.post("/auth/login", json={"email": "inactive@test.local", "password": PASSWORD})

    assert response.status_code == 401


def test_logout_clears_the_session(http_client: TestClient) -> None:
    login(http_client, ADMIN_EMAIL)

    response = http_client.post("/auth/logout")

    assert response.status_code == 204
    assert f'{SESSION_COOKIE}=""' in response.headers["set-cookie"]
    assert http_client.get("/auth/me").status_code == 401


def test_deactivated_users_lose_their_session(http_client: TestClient) -> None:
    login(http_client, ADMIN_EMAIL)
    admin_token = http_client.cookies[SESSION_COOKIE]
    login(http_client, SUPER_ADMIN_EMAIL)
    admin_id = next(user["id"] for user in http_client.get("/users").json()["items"] if user["email"] == ADMIN_EMAIL)
    assert http_client.patch(f"/users/{admin_id}", json={"is_active": False}).status_code == 200

    http_client.cookies.set(SESSION_COOKIE, admin_token)

    assert http_client.get("/auth/me").status_code == 401
    assert http_client.get("/sneakers").status_code == 401
