from typing import Any
from uuid import uuid7

import pytest
from fastapi.testclient import TestClient

from support.image_storage import InMemoryImageStorage

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


@pytest.fixture
def references(client: TestClient) -> dict[str, str]:
    brand = client.post("/brands", json={"name": "Nike"}).json()
    category = client.post("/categories", json={"name": "Running"}).json()
    return {"brand_id": brand["id"], "category_id": category["id"]}


def sneaker_payload(references: dict[str, str], **overrides: Any) -> dict[str, Any]:
    payload = {
        "name": "Air Max 90",
        "description": "Classic runner",
        "gender": "unisex",
        "price": "130.00",
        "currency": "USD",
        **references,
    }
    return payload | overrides


def create_sneaker(client: TestClient, references: dict[str, str], **overrides: Any) -> dict[str, Any]:
    response = client.post("/sneakers", json=sneaker_payload(references, **overrides))
    assert response.status_code == 201, response.text
    return response.json()


def add_colorway(client: TestClient, sneaker_id: str, **overrides: Any) -> dict[str, Any]:
    body = {"name": "Infrared", "color_code": "#ff0000", "sku": "am90-inf"} | overrides
    response = client.post(f"/sneakers/{sneaker_id}/colorways", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def upload_image(client: TestClient, sneaker_id: str, alt: str = "") -> dict[str, Any]:
    response = client.post(
        f"/sneakers/{sneaker_id}/images",
        files={"file": ("front.png", PNG, "image/png")},
        data={"alt": alt},
    )
    assert response.status_code == 201, response.text
    return response.json()


def make_publishable(client: TestClient, references: dict[str, str], **overrides: Any) -> dict[str, Any]:
    sneaker = create_sneaker(client, references, **overrides)
    colorway = add_colorway(client, sneaker["id"])["colorways"][0]
    client.put(f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}/sizes/42", json={"stock": 3})
    return upload_image(client, sneaker["id"])


def test_sneaker_crud_flow(client: TestClient, references: dict[str, str]) -> None:
    sneaker = create_sneaker(client, references)

    assert sneaker["slug"] == "air-max-90"
    assert sneaker["status"] == "draft"
    assert sneaker["base_price"] == {"amount": "130.00", "currency": "USD"}
    assert client.get(f"/sneakers/{sneaker['id']}").json() == sneaker

    updated = client.put(f"/sneakers/{sneaker['id']}", json=sneaker_payload(references, name="Air Max 95"))
    assert updated.status_code == 200
    assert updated.json()["slug"] == "air-max-95"

    assert client.get("/sneakers").json()["items"] == [updated.json()]
    assert client.delete(f"/sneakers/{sneaker['id']}").status_code == 204
    assert client.get(f"/sneakers/{sneaker['id']}").status_code == 404


def test_create_sneaker_with_unknown_brand_returns_not_found(client: TestClient, references: dict[str, str]) -> None:
    response = client.post("/sneakers", json=sneaker_payload(references, brand_id=str(uuid7())))

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_create_sneaker_with_duplicated_slug_returns_conflict(client: TestClient, references: dict[str, str]) -> None:
    create_sneaker(client, references)

    response = client.post("/sneakers", json=sneaker_payload(references, name="AIR MAX 90"))

    assert response.status_code == 409


@pytest.mark.parametrize(
    "overrides",
    [{"price": "-1"}, {"currency": "usd"}, {"gender": "aliens"}, {"name": "  "}, {"slug": "Not A Slug"}],
    ids=["negative-price", "invalid-currency", "invalid-gender", "blank-name", "invalid-slug"],
)
def test_create_sneaker_with_invalid_data_returns_unprocessable(
    client: TestClient, references: dict[str, str], overrides: dict[str, Any]
) -> None:
    assert client.post("/sneakers", json=sneaker_payload(references, **overrides)).status_code == 422


def test_colorway_and_size_flow(client: TestClient, references: dict[str, str]) -> None:
    sneaker = create_sneaker(client, references)
    colorway = add_colorway(client, sneaker["id"], price_override="180.00")["colorways"][0]

    assert colorway["sku"] == "AM90-INF"
    assert colorway["effective_price"] == {"amount": "180.00", "currency": "USD"}

    with_size = client.put(f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}/sizes/42.5", json={"stock": 4})
    assert with_size.json()["colorways"][0]["sizes"] == [{"size": "42.5", "stock": 4}]

    renamed = client.put(
        f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}",
        json={"name": "Infrared 2", "color_code": "#FF0000", "sku": "AM90-INF"},
    )
    assert renamed.json()["colorways"][0]["price_override"] is None

    without_size = client.delete(f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}/sizes/42.5")
    assert without_size.json()["colorways"][0]["sizes"] == []
    assert client.delete(f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}").json()["colorways"] == []


def test_duplicated_sku_returns_conflict(client: TestClient, references: dict[str, str]) -> None:
    first = create_sneaker(client, references)
    second = create_sneaker(client, references, name="Air Max 97")
    add_colorway(client, first["id"])

    response = client.post(f"/sneakers/{second['id']}/colorways", json={
        "name": "Infrared",
        "color_code": "#ff0000",
        "sku": "AM90-INF",
    })

    assert response.status_code == 409


def test_negative_stock_returns_unprocessable(client: TestClient, references: dict[str, str]) -> None:
    sneaker = create_sneaker(client, references)
    colorway = add_colorway(client, sneaker["id"])["colorways"][0]
    client.put(f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}/sizes/42", json={"stock": 5})

    response = client.put(f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}/sizes/42", json={"stock": -1})

    assert response.status_code == 422
    stored = client.get(f"/sneakers/{sneaker['id']}").json()
    assert stored["colorways"][0]["sizes"] == [{"size": "42.0", "stock": 5}]


def test_publish_without_primary_image_returns_conflict(client: TestClient, references: dict[str, str]) -> None:
    sneaker = create_sneaker(client, references)
    colorway = add_colorway(client, sneaker["id"])["colorways"][0]
    client.put(f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}/sizes/42", json={"stock": 1})

    response = client.post(f"/sneakers/{sneaker['id']}/publish")

    assert response.status_code == 409
    assert "primary image" in response.json()["detail"]


def test_publication_lifecycle(client: TestClient, references: dict[str, str]) -> None:
    sneaker = make_publishable(client, references)

    assert client.post(f"/sneakers/{sneaker['id']}/publish").json()["status"] == "active"
    assert client.post(f"/sneakers/{sneaker['id']}/publish").status_code == 409
    assert client.post(f"/sneakers/{sneaker['id']}/archive").json()["status"] == "archived"
    assert client.post(f"/sneakers/{sneaker['id']}/unarchive").json()["status"] == "draft"


def test_image_flow_uses_injected_storage(
    client: TestClient, references: dict[str, str], image_storage: InMemoryImageStorage
) -> None:
    sneaker = create_sneaker(client, references)
    first = upload_image(client, sneaker["id"], alt="Front")["images"][0]
    images = upload_image(client, sneaker["id"])["images"]
    second = images[1]

    assert (first["alt"], first["position"], first["is_primary"]) == ("Front", 0, True)
    assert len(image_storage.uploaded) == 2

    reordered = client.put(
        f"/sneakers/{sneaker['id']}/images/order", json={"image_ids": [second["id"], first["id"]]}
    )
    assert [image["id"] for image in reordered.json()["images"]] == [second["id"], first["id"]]

    marked = client.post(f"/sneakers/{sneaker['id']}/images/{second['id']}/primary")
    assert [image["is_primary"] for image in marked.json()["images"]] == [True, False]

    deleted = client.delete(f"/sneakers/{sneaker['id']}/images/{second['id']}")
    assert [image["id"] for image in deleted.json()["images"]] == [first["id"]]
    assert image_storage.deleted == [second["public_id"]]


def test_upload_rejects_invalid_file_without_touching_storage(
    client: TestClient, references: dict[str, str], image_storage: InMemoryImageStorage
) -> None:
    sneaker = create_sneaker(client, references)

    response = client.post(
        f"/sneakers/{sneaker['id']}/images", files={"file": ("notes.txt", b"not an image", "text/plain")}
    )

    assert response.status_code == 422
    assert image_storage.uploaded == []


def test_delete_sneaker_removes_its_images_from_storage(
    client: TestClient, references: dict[str, str], image_storage: InMemoryImageStorage
) -> None:
    sneaker = make_publishable(client, references)

    assert client.delete(f"/sneakers/{sneaker['id']}").status_code == 204
    assert image_storage.deleted == [sneaker["images"][0]["public_id"]]


def test_filters_and_pagination(client: TestClient, references: dict[str, str]) -> None:
    make_publishable(client, references)
    create_sneaker(client, references, name="Pegasus", price="80.00")
    create_sneaker(client, references, name="Vomero", price="90.00", gender="men")

    listed = client.get("/sneakers", params={"q": "air", "in_stock": True, "shoe_size": "42"}).json()
    assert [item["name"] for item in listed["items"]] == ["Air Max 90"]

    by_price = client.get("/sneakers", params={"min_price": "100", "currency": "USD", "sort": "price"}).json()
    assert [item["name"] for item in by_price["items"]] == ["Air Max 90"]

    by_gender = client.get("/sneakers", params={"gender": "men"}).json()
    assert [item["name"] for item in by_gender["items"]] == ["Vomero"]

    paginated = client.get("/sneakers", params={"sort": "name", "page": 2, "size": 2}).json()
    assert (paginated["total"], paginated["pages"], len(paginated["items"])) == (3, 2, 1)


def test_price_filter_without_currency_returns_unprocessable(client: TestClient) -> None:
    assert client.get("/sneakers", params={"min_price": "100"}).status_code == 422


def test_delete_brand_and_category_in_use_returns_conflict(client: TestClient, references: dict[str, str]) -> None:
    create_sneaker(client, references)

    assert client.delete(f"/brands/{references['brand_id']}").status_code == 409
    assert client.delete(f"/categories/{references['category_id']}").status_code == 409


def test_unknown_ids_return_not_found(client: TestClient, references: dict[str, str]) -> None:
    sneaker = create_sneaker(client, references)
    unknown = str(uuid7())

    assert client.get(f"/sneakers/{unknown}").status_code == 404
    assert client.post(f"/sneakers/{unknown}/publish").status_code == 404
    assert client.delete(f"/sneakers/{sneaker['id']}/colorways/{unknown}").status_code == 404
    assert client.delete(f"/sneakers/{sneaker['id']}/images/{unknown}").status_code == 404


def test_sneaker_sales_content_round_trip(client: TestClient, references: dict[str, str]) -> None:
    content = {
        "reference": "als-am90-001",
        "specs": {"material": "Mesh", "technology": "Air", "weight": "310 g", "cushioning": "Media"},
        "usage": "Running diario",
        "testimonial": {"quote": "Muy cómodas", "author": "Ana, talla 38"},
    }
    sneaker = create_sneaker(client, references, **content)

    assert sneaker["reference"] == "ALS-AM90-001"
    assert sneaker["specs"] == content["specs"]
    assert sneaker["usage"] == "Running diario"
    assert sneaker["testimonial"] == content["testimonial"]

    cleared = client.put(f"/sneakers/{sneaker['id']}", json=sneaker_payload(references)).json()
    assert (cleared["reference"], cleared["usage"], cleared["testimonial"]) == (None, "", None)
    assert cleared["specs"] == {"material": "", "technology": "", "weight": "", "cushioning": ""}


def test_duplicated_reference_is_a_conflict(client: TestClient, references: dict[str, str]) -> None:
    create_sneaker(client, references, reference="ALS-001")

    response = client.post("/sneakers", json=sneaker_payload(references, name="Air Max 95", reference="als-001"))

    assert response.status_code == 409


def test_get_sneaker_by_slug(client: TestClient, references: dict[str, str]) -> None:
    sneaker = create_sneaker(client, references)

    assert client.get("/sneakers/by-slug/air-max-90").json() == sneaker
    assert client.get("/sneakers/by-slug/missing").status_code == 404


def test_list_sneakers_accepts_repeated_filters(client: TestClient, references: dict[str, str]) -> None:
    create_sneaker(client, references, gender="men")
    create_sneaker(client, references, name="Cortez", gender="women")
    create_sneaker(client, references, name="Kids Run", gender="kids")

    listed = client.get("/sneakers", params=[("gender", "men"), ("gender", "women"), ("sort", "name")]).json()

    assert [item["name"] for item in listed["items"]] == ["Air Max 90", "Cortez"]
    assert client.get("/sneakers", params={"color": "blue"}).status_code == 422


def test_public_catalog_only_exposes_published_sneakers(client: TestClient, references: dict[str, str]) -> None:
    published = make_publishable(client, references)
    client.post(f"/sneakers/{published['id']}/publish")
    create_sneaker(client, references, name="Draft Runner")

    listed = client.get("/catalog/sneakers", params={"status": "draft"}).json()

    assert [item["slug"] for item in listed["items"]] == ["air-max-90"]
    assert client.get("/catalog/sneakers/air-max-90").json()["status"] == "active"
    assert client.get("/catalog/sneakers/draft-runner").status_code == 404


def test_public_catalog_facets(client: TestClient, references: dict[str, str]) -> None:
    published = make_publishable(client, references)
    client.post(f"/sneakers/{published['id']}/publish")
    create_sneaker(client, references, name="Draft Runner", currency="EUR")

    facets = client.get("/catalog/facets").json()

    assert facets == {
        "brands": [{"value": "nike", "label": "Nike", "count": 1}],
        "categories": [{"value": "running", "label": "Running", "count": 1}],
        "genders": [{"value": "unisex", "label": "unisex", "count": 1}],
        "sizes": [{"value": "42", "label": "42", "count": 1}],
        "colors": [{"value": "#FF0000", "label": "Infrared", "count": 1}],
        "currencies": ["USD"],
    }
