from uuid import uuid7

from saury_backend.catalog.application.ports.image_storage import ImageStorageError, StoredImage


class InMemoryImageStorage:
    def __init__(self) -> None:
        self.images: dict[str, bytes] = {}
        self.uploaded: list[StoredImage] = []
        self.deleted: list[str] = []
        self.fail_on_upload = False
        self.fail_on_delete = False

    async def upload(self, content: bytes, filename: str, folder: str) -> StoredImage:
        if self.fail_on_upload:
            raise ImageStorageError(f"upload failed for {filename}")
        public_id = f"{folder}/{uuid7().hex}"
        image = StoredImage(public_id=public_id, url=f"https://images.test/{public_id}")
        self.images[public_id] = content
        self.uploaded.append(image)
        return image

    async def delete(self, public_id: str) -> None:
        if self.fail_on_delete:
            raise ImageStorageError(f"delete failed for {public_id}")
        self.images.pop(public_id, None)
        self.deleted.append(public_id)
