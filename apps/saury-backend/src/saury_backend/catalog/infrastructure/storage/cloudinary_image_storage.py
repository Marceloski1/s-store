from functools import partial

import cloudinary.exceptions
import cloudinary.uploader
import cloudinary.utils
from anyio import to_thread

from saury_backend.catalog.application.ports.image_storage import ImageStorageError, StoredImage

_DELIVERY_TRANSFORMATION = {"fetch_format": "auto", "quality": "auto"}
_DELETED_RESULTS = {"ok", "not found"}


class CloudinaryImageStorage:
    def __init__(self, cloud_name: str, api_key: str, api_secret: str) -> None:
        if not (cloud_name and api_key and api_secret):
            raise ValueError("Cloudinary cloud name, api key and api secret are required")
        self._credentials = {"cloud_name": cloud_name, "api_key": api_key, "api_secret": api_secret}

    async def upload(self, content: bytes, filename: str, folder: str) -> StoredImage:
        upload = partial(
            cloudinary.uploader.upload,
            content,
            filename=filename,
            folder=folder,
            resource_type="image",
            **self._credentials,
        )
        try:
            result = await to_thread.run_sync(upload)
        except cloudinary.exceptions.Error as error:
            raise ImageStorageError(f"Could not upload image {filename}") from error
        return StoredImage(public_id=result["public_id"], url=self._delivery_url(result["public_id"], result["version"]))

    async def delete(self, public_id: str) -> None:
        destroy = partial(
            cloudinary.uploader.destroy,
            public_id,
            invalidate=True,
            resource_type="image",
            **self._credentials,
        )
        try:
            result = await to_thread.run_sync(destroy)
        except cloudinary.exceptions.Error as error:
            raise ImageStorageError(f"Could not delete image {public_id}") from error
        if result.get("result") not in _DELETED_RESULTS:
            raise ImageStorageError(f"Could not delete image {public_id}: {result.get('result')}")

    def _delivery_url(self, public_id: str, version: int) -> str:
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            version=version,
            secure=True,
            cloud_name=self._credentials["cloud_name"],
            **_DELIVERY_TRANSFORMATION,
        )
        return url
