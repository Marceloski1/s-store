from uuid import uuid7

from fastapi.testclient import TestClient


def test_brand_crud_flow(client: TestClient) -> None:
    created = client.post("/brands", json={"name": "New Balance"})
    assert created.status_code == 201
    brand = created.json()
    assert brand["slug"] == "new-balance"

    assert client.get(f"/brands/{brand['id']}").json() == brand

    updated = client.put(f"/brands/{brand['id']}", json={"name": "New Balance", "slug": "nb"})
    assert updated.status_code == 200
    assert updated.json() == {**brand, "slug": "nb"}

    listed = client.get("/brands")
    assert listed.json() == {"items": [updated.json()], "total": 1, "page": 1, "size": 20, "pages": 1}

    assert client.delete(f"/brands/{brand['id']}").status_code == 204
    assert client.get(f"/brands/{brand['id']}").status_code == 404


def test_list_brands_paginates_sorted_by_name(client: TestClient) -> None:
    for name in ("Puma", "Adidas", "Nike"):
        client.post("/brands", json={"name": name})

    response = client.get("/brands", params={"page": 2, "size": 2})

    assert [brand["name"] for brand in response.json()["items"]] == ["Puma"]
    assert response.json()["pages"] == 2


def test_create_brand_with_duplicated_slug_returns_conflict(client: TestClient) -> None:
    client.post("/brands", json={"name": "Nike"})

    response = client.post("/brands", json={"name": "Nike"})

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Brand slug 'nike' already exists",
        "code": "BRAND_SLUG_ALREADY_EXISTS",
        "params": {"slug": "nike"},
    }


def test_create_brand_with_invalid_payload_returns_unprocessable(client: TestClient) -> None:
    response = client.post("/brands", json={"name": " ", "slug": "Bad Slug"})

    assert response.status_code == 422


def test_list_brands_rejects_size_over_limit(client: TestClient) -> None:
    assert client.get("/brands", params={"size": 101}).status_code == 422


def test_update_missing_brand_returns_not_found(client: TestClient) -> None:
    assert client.put(f"/brands/{uuid7()}", json={"name": "Nike"}).status_code == 404
