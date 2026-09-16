from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from saury_backend.catalog.presentation.http.dependencies import ImageStorageDep
from saury_backend.catalog.presentation.http.image_upload import MAX_IMAGE_SIZE_BYTES, ImageUploadDep
from support.image_storage import InMemoryImageStorage

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 16


@pytest.fixture
def upload_client(app: FastAPI) -> Iterator[TestClient]:
    @app.post("/test-image-uploads", status_code=201)
    async def upload_image(image: ImageUploadDep, storage: ImageStorageDep) -> dict[str, str]:
        stored = await storage.upload(image.content, image.filename, "sauri-store/test")
        return {"public_id": stored.public_id, "url": stored.url}

    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("content", "content_type"),
    [(PNG, "image/png"), (JPEG, "image/jpeg"), (WEBP, "image/webp")],
)
def test_valid_image_is_uploaded_with_overridden_storage(
    upload_client: TestClient, image_storage: InMemoryImageStorage, content: bytes, content_type: str
) -> None:
    response = upload_client.post("/test-image-uploads", files={"file": ("air-max", content, content_type)})

    assert response.status_code == 201
    [stored] = image_storage.uploaded
    assert response.json() == {"public_id": stored.public_id, "url": stored.url}
    assert image_storage.images[stored.public_id] == content


@pytest.mark.parametrize(
    ("content", "content_type"),
    [
        (b"GIF89a" + b"\x00" * 16, "image/gif"),
        (b"not an image", "text/plain"),
        (b"not an image", "image/png"),
        (JPEG, "image/png"),
        (b"", "image/png"),
        (PNG + b"\x00" * MAX_IMAGE_SIZE_BYTES, "image/png"),
    ],
    ids=["gif", "text", "fake-png", "mismatched-type", "empty", "too-large"],
)
def test_invalid_image_is_rejected_without_calling_storage(
    upload_client: TestClient, image_storage: InMemoryImageStorage, content: bytes, content_type: str
) -> None:
    response = upload_client.post("/test-image-uploads", files={"file": ("file", content, content_type)})

    assert response.status_code == 422
    assert image_storage.uploaded == []


def test_missing_file_is_rejected(upload_client: TestClient, image_storage: InMemoryImageStorage) -> None:
    response = upload_client.post("/test-image-uploads")

    assert response.status_code == 422
    assert image_storage.uploaded == []
