from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, UploadFile

from saury_backend.catalog.domain.errors import InvalidImage

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})


@dataclass(frozen=True, slots=True)
class ImageUpload:
    content: bytes
    filename: str
    content_type: str


def _detect_image_type(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None




async def read_image_upload(file: UploadFile) -> ImageUpload:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise InvalidImage(f"Unsupported image type: {file.content_type}", reason="UNSUPPORTED_TYPE")
    content = await file.read(MAX_IMAGE_SIZE_BYTES + 1)
    if not content:
        raise InvalidImage("Image file is empty", reason="EMPTY")
    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise InvalidImage(f"Image exceeds the maximum size of {MAX_IMAGE_SIZE_BYTES} bytes", reason="TOO_LARGE")
    if _detect_image_type(content) != file.content_type:
        raise InvalidImage("Image content does not match its declared type", reason="CONTENT_MISMATCH")
    return ImageUpload(content=content, filename=file.filename or "image", content_type=file.content_type)


ImageUploadDep = Annotated[ImageUpload, Depends(read_image_upload)]
