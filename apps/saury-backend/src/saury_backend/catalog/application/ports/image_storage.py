from dataclasses import dataclass
from typing import Protocol

from shared.domain.errors import ExternalServiceError

from saury_backend.catalog.domain.error_codes import CatalogErrorCode


class ImageStorageError(ExternalServiceError):
    code = CatalogErrorCode.IMAGE_STORAGE_ERROR


@dataclass(frozen=True, slots=True)
class StoredImage:
    public_id: str
    url: str


class ImageStorage(Protocol):
    async def upload(self, content: bytes, filename: str, folder: str) -> StoredImage: ...

    async def delete(self, public_id: str) -> None: ...
