from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StoredImage:
    public_id: str
    url: str


class ImageStorage(Protocol):
    async def upload(self, content: bytes, filename: str, folder: str) -> StoredImage: ...

    async def delete(self, public_id: str) -> None: ...
