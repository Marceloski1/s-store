from typing import Any
from uuid import uuid7

from fastapi.testclient import TestClient

from support.identity import SUPER_ADMIN_EMAIL, login
from support.image_storage import InMemoryImageStorage

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def create_sneaker(client: TestClient) -> dict[str, Any]:
    brand = client.post("/brands", json={"name": "Nike"}).json()
    category = client.post("/categories", json={"name": "Running"}).json()
    response = client.post(
        "/sneakers",
        json={
            "name": "Air Max 90",
            "gender": "UNISEX",
            "price": "130.00",
            "currency": "USD",
            "brand_id": brand["id"],
            "category_id": category["id"],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_not_found_errors_carry_code_and_params(client: TestClient) -> None:
    missing = uuid7()

    response = client.get(f"/sneakers/{missing}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Sneaker '{missing}' not found",
        "code": "SNEAKER_NOT_FOUND",
        "params": {"id": str(missing)},
    }


def test_conflicts_explain_the_missing_publication_requirement(client: TestClient) -> None:
    sneaker = create_sneaker(client)

    response = client.post(f"/sneakers/{sneaker['id']}/publish")

    assert response.status_code == 409
    assert (response.json()["code"], response.json()["params"]) == ("SNEAKER_NEEDS_PRIMARY_IMAGE", {})


def test_request_validation_errors_list_each_field(client: TestClient) -> None:
    response = client.post("/brands", json={"name": ""})

    assert response.status_code == 422
    body = response.json()
    assert (body["code"], body["params"]) == ("VALIDATION_ERROR", {})
    assert body["errors"] == [
        {"field": "name", "location": "body", "type": "string_too_short", "ctx": {"min_length": 1}}
    ]


def test_query_validation_errors_report_their_location(client: TestClient) -> None:
    response = client.get("/sneakers", params={"gender": "ALIENS"})

    assert response.status_code == 422
    [error] = response.json()["errors"]
    assert (error["field"], error["location"], error["type"]) == ("gender.0", "query", "enum")


def test_domain_validation_errors_share_the_422_shape(client: TestClient) -> None:
    sneaker = create_sneaker(client)
    colorway = client.post(
        f"/sneakers/{sneaker['id']}/colorways", json={"name": "Red", "color_code": "#FF0000", "sku": "AM-RED"}
    ).json()["colorways"][0]

    response = client.put(f"/sneakers/{sneaker['id']}/colorways/{colorway['id']}/sizes/42.3", json={"stock": 1})

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Shoe size must be a positive EU size in steps of 0.5 up to 99.5",
        "code": "INVALID_SHOE_SIZE",
        "params": {"value": "42.3", "max": "99.5"},
        "errors": [],
    }


def test_invalid_uploads_report_the_reason(client: TestClient) -> None:
    sneaker = create_sneaker(client)

    response = client.post(
        f"/sneakers/{sneaker['id']}/images", files={"file": ("front.png", b"not an image", "image/png")}
    )

    assert response.status_code == 422
    assert (response.json()["code"], response.json()["params"]) == ("IMAGE_INVALID", {"reason": "CONTENT_MISMATCH"})


def test_storage_failures_are_bad_gateway(client: TestClient, image_storage: InMemoryImageStorage) -> None:
    sneaker = create_sneaker(client)
    image_storage.fail_on_upload = True

    response = client.post(f"/sneakers/{sneaker['id']}/images", files={"file": ("front.png", PNG, "image/png")})

    assert response.status_code == 502
    assert response.json()["code"] == "IMAGE_STORAGE_ERROR"


def test_authentication_and_authorization_errors_are_coded(http_client: TestClient) -> None:
    anonymous = http_client.get("/sneakers")
    assert (anonymous.status_code, anonymous.json()["code"]) == (401, "NOT_AUTHENTICATED")

    login(http_client, SUPER_ADMIN_EMAIL)
    forbidden = http_client.get("/sneakers")
    assert (forbidden.status_code, forbidden.json()["code"], forbidden.json()["params"]) == (
        403,
        "INSUFFICIENT_ROLE",
        {"role": "ADMIN"},
    )

    me = http_client.get("/auth/me").json()
    self_delete = http_client.delete(f"/users/{me['id']}")
    assert (self_delete.status_code, self_delete.json()["code"], self_delete.json()["params"]) == (
        409,
        "CANNOT_MANAGE_USER",
        {"reason": "SELF"},
    )


def test_unknown_routes_use_the_generic_not_found_code(client: TestClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found", "code": "NOT_FOUND", "params": {}}


def test_openapi_exposes_typed_error_models(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    schemas = schema["components"]["schemas"]

    codes = schemas["ErrorCode"]["enum"]
    assert {"VALIDATION_ERROR", "SNEAKER_NOT_FOUND", "INVALID_CREDENTIALS", "INVALID_SHOE_SIZE"} <= set(codes)
    assert all(code == code.upper() for code in codes)
    assert "HTTPValidationError" not in schemas
    create_sneaker_responses = schema["paths"]["/sneakers"]["post"]["responses"]
    assert create_sneaker_responses["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ValidationErrorResponse"
    }
    assert create_sneaker_responses["404"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ErrorResponse"
    }
