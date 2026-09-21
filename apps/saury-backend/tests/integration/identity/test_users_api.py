from typing import Any

import pytest
from fastapi.testclient import TestClient

from support.identity import ADMIN_EMAIL, PASSWORD, SUPER_ADMIN_EMAIL, login


@pytest.fixture
def super_admin(http_client: TestClient) -> TestClient:
    login(http_client, SUPER_ADMIN_EMAIL)
    return http_client


def find_user(client: TestClient, email: str) -> dict[str, Any]:
    return next(user for user in client.get("/users", params={"size": 100}).json()["items"] if user["email"] == email)


def test_super_admin_creates_admin_users(super_admin: TestClient) -> None:
    response = super_admin.post(
        "/users", json={"email": "Nuevo@Test.local", "name": "Nuevo Admin", "password": "Password123!"}
    )

    assert response.status_code == 201
    created = response.json()
    assert (created["email"], created["name"], created["role"], created["is_active"]) == (
        "nuevo@test.local",
        "Nuevo Admin",
        "ADMIN",
        True,
    )
    listed = super_admin.get("/users").json()
    assert listed["total"] == 3
    assert "nuevo@test.local" in [user["email"] for user in listed["items"]]

    login(super_admin, "nuevo@test.local", "Password123!")
    assert super_admin.get("/auth/me").json()["role"] == "ADMIN"


def test_create_user_validates_input(super_admin: TestClient) -> None:
    duplicated = super_admin.post("/users", json={"email": ADMIN_EMAIL, "name": "Otro", "password": PASSWORD})
    weak = super_admin.post("/users", json={"email": "weak@test.local", "name": "Weak", "password": "short"})
    invalid_email = super_admin.post("/users", json={"email": "not-an-email", "name": "X", "password": PASSWORD})

    assert (duplicated.status_code, weak.status_code, invalid_email.status_code) == (409, 422, 422)


def test_super_admin_updates_admin_users(super_admin: TestClient) -> None:
    admin = find_user(super_admin, ADMIN_EMAIL)

    renamed = super_admin.patch(f"/users/{admin['id']}", json={"name": "Eduardo M.", "password": "NewPassword1!"})

    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Eduardo M."
    login(super_admin, ADMIN_EMAIL, "NewPassword1!")
    assert super_admin.get("/auth/me").json()["name"] == "Eduardo M."


def test_super_admins_cannot_be_modified_or_deleted(super_admin: TestClient) -> None:
    me = find_user(super_admin, SUPER_ADMIN_EMAIL)

    assert super_admin.patch(f"/users/{me['id']}", json={"is_active": False}).status_code == 409
    assert super_admin.delete(f"/users/{me['id']}").status_code == 409


def test_super_admin_deletes_admin_users(super_admin: TestClient) -> None:
    admin = find_user(super_admin, ADMIN_EMAIL)

    assert super_admin.delete(f"/users/{admin['id']}").status_code == 204
    assert super_admin.delete(f"/users/{admin['id']}").status_code == 404
    assert super_admin.post("/auth/login", json={"email": ADMIN_EMAIL, "password": PASSWORD}).status_code == 401
