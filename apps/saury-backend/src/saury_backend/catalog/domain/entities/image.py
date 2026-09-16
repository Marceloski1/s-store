from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid7

from shared.domain.errors import ValidationError
from shared.domain.validation import require_text

IMAGE_ALT_MAX_LENGTH = 200
IMAGE_URL_MAX_LENGTH = 500
IMAGE_PUBLIC_ID_MAX_LENGTH = 255


def _clean_alt(alt: str) -> str:
    cleaned = alt.strip()
    if len(cleaned) > IMAGE_ALT_MAX_LENGTH:
        raise ValidationError(f"alt must be at most {IMAGE_ALT_MAX_LENGTH} characters")
    return cleaned


@dataclass(slots=True)
class Image:
    id: UUID
    public_id: str
    url: str
    alt: str
    position: int
    is_primary: bool = False

    def __post_init__(self) -> None:
        self.public_id = require_text(self.public_id, field="public_id", max_length=IMAGE_PUBLIC_ID_MAX_LENGTH)
        self.url = require_text(self.url, field="url", max_length=IMAGE_URL_MAX_LENGTH)
        self.alt = _clean_alt(self.alt)
        if self.position < 0:
            raise ValidationError("position must not be negative")

    @classmethod
    def create(cls, public_id: str, url: str, alt: str, position: int) -> Self:
        return cls(id=uuid7(), public_id=public_id, url=url, alt=alt, position=position)
