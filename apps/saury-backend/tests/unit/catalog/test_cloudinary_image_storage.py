import threading
from typing import Any

import cloudinary.exceptions
import cloudinary.uploader
import pytest

from saury_backend.catalog.application.ports.image_storage import ImageStorage, ImageStorageError
from saury_backend.catalog.infrastructure.storage.cloudinary_image_storage import CloudinaryImageStorage

CREDENTIALS = {"cloud_name": "demo", "api_key": "key", "api_secret": "secret"}


class SdkCall:
    def __init__(self, response: dict[str, Any] | None = None, error: Exception | None = None) -> None:
        self.response = response or {}
        self.error = error
        self.args: tuple[Any, ...] = ()
        self.options: dict[str, Any] = {}
        self.thread_id: int | None = None

    def __call__(self, *args: Any, **options: Any) -> dict[str, Any]:
        self.args = args
        self.options = options
        self.thread_id = threading.get_ident()
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture
def storage() -> ImageStorage:
    return CloudinaryImageStorage(**CREDENTIALS)


@pytest.mark.parametrize("missing", ["cloud_name", "api_key", "api_secret"])
def test_requires_all_credentials(missing: str) -> None:
    with pytest.raises(ValueError):
        CloudinaryImageStorage(**(CREDENTIALS | {missing: ""}))


async def test_upload_sends_content_with_credentials_in_a_worker_thread(
    storage: ImageStorage, monkeypatch: pytest.MonkeyPatch
) -> None:
    upload = SdkCall({"public_id": "sauri-store/test/abc", "version": 1789579024})
    monkeypatch.setattr(cloudinary.uploader, "upload", upload)

    await storage.upload(b"png-bytes", "air-max.png", "sauri-store/test")

    assert upload.args == (b"png-bytes",)
    assert upload.options == {
        "filename": "air-max.png",
        "folder": "sauri-store/test",
        "resource_type": "image",
        **CREDENTIALS,
    }
    assert upload.thread_id != threading.get_ident()


async def test_upload_returns_https_url_with_delivery_transformations(
    storage: ImageStorage, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cloudinary.uploader, "upload", SdkCall({"public_id": "sauri-store/test/abc", "version": 1789579024}))

    image = await storage.upload(b"png-bytes", "air-max.png", "sauri-store/test")

    assert image.public_id == "sauri-store/test/abc"
    assert image.url == "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto/v1789579024/sauri-store/test/abc"


async def test_upload_wraps_sdk_errors(storage: ImageStorage, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cloudinary.uploader, "upload", SdkCall(error=cloudinary.exceptions.Error("boom")))

    with pytest.raises(ImageStorageError):
        await storage.upload(b"png-bytes", "air-max.png", "sauri-store/test")


@pytest.mark.parametrize("result", ["ok", "not found"])
async def test_delete_destroys_and_invalidates_image(
    storage: ImageStorage, monkeypatch: pytest.MonkeyPatch, result: str
) -> None:
    destroy = SdkCall({"result": result})
    monkeypatch.setattr(cloudinary.uploader, "destroy", destroy)

    await storage.delete("sauri-store/test/abc")

    assert destroy.args == ("sauri-store/test/abc",)
    assert destroy.options == {"invalidate": True, "resource_type": "image", **CREDENTIALS}
    assert destroy.thread_id != threading.get_ident()


async def test_delete_fails_on_unexpected_result(storage: ImageStorage, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cloudinary.uploader, "destroy", SdkCall({"result": "error"}))

    with pytest.raises(ImageStorageError):
        await storage.delete("sauri-store/test/abc")


async def test_delete_wraps_sdk_errors(storage: ImageStorage, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cloudinary.uploader, "destroy", SdkCall(error=cloudinary.exceptions.Error("boom")))

    with pytest.raises(ImageStorageError):
        await storage.delete("sauri-store/test/abc")
