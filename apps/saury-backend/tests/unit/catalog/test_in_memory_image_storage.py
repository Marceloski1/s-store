import pytest

from saury_backend.catalog.application.ports.image_storage import ImageStorage

from .conftest import ImageStorageError, InMemoryImageStorage


def as_port(storage: InMemoryImageStorage) -> ImageStorage:
    return storage


async def test_upload_stores_content_under_folder(image_storage: InMemoryImageStorage) -> None:
    image = await as_port(image_storage).upload(b"png-bytes", "air-max.png", "sauri-store/test")

    assert image.public_id.startswith("sauri-store/test/")
    assert image.url == f"https://images.test/{image.public_id}"
    assert image_storage.images[image.public_id] == b"png-bytes"
    assert image_storage.uploaded == [image]


async def test_delete_removes_content_and_records_it(image_storage: InMemoryImageStorage) -> None:
    image = await image_storage.upload(b"png-bytes", "air-max.png", "sauri-store/test")

    await image_storage.delete(image.public_id)

    assert image.public_id not in image_storage.images
    assert image_storage.deleted == [image.public_id]


async def test_upload_can_simulate_failure(image_storage: InMemoryImageStorage) -> None:
    image_storage.fail_on_upload = True

    with pytest.raises(ImageStorageError):
        await image_storage.upload(b"png-bytes", "air-max.png", "sauri-store/test")

    assert image_storage.uploaded == []


async def test_delete_can_simulate_failure(image_storage: InMemoryImageStorage) -> None:
    image = await image_storage.upload(b"png-bytes", "air-max.png", "sauri-store/test")
    image_storage.fail_on_delete = True

    with pytest.raises(ImageStorageError):
        await image_storage.delete(image.public_id)

    assert image.public_id in image_storage.images
    assert image_storage.deleted == []
