from uuid import uuid7

from fastapi.testclient import TestClient


def test_category_crud_flow(client: TestClient) -> None:
    created = client.post("/categories", json={"name": "Trail Running"})
    assert created.status_code == 201
    category = created.json()
    assert category["slug"] == "trail-running"

    updated = client.put(f"/categories/{category['id']}", json={"name": "Running"})
    assert updated.json() == {**category, "name": "Running", "slug": "running"}

    assert client.get("/categories").json()["items"] == [updated.json()]

    assert client.delete(f"/categories/{category['id']}").status_code == 204
    assert client.get(f"/categories/{category['id']}").status_code == 404


def test_update_category_with_slug_of_another_returns_conflict(client: TestClient) -> None:
    client.post("/categories", json={"name": "Running"})
    lifestyle = client.post("/categories", json={"name": "Lifestyle"}).json()

    response = client.put(f"/categories/{lifestyle['id']}", json={"name": "Lifestyle", "slug": "running"})

    assert response.status_code == 409


def test_delete_missing_category_returns_not_found(client: TestClient) -> None:
    assert client.delete(f"/categories/{uuid7()}").status_code == 404
