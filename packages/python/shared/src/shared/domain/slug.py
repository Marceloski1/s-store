import re
import unicodedata
from dataclasses import dataclass
from typing import Self

from shared.domain.errors import CommonErrorCode, ValidationError

SLUG_MAX_LENGTH = 120
SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"

_SLUG_REGEX = re.compile(SLUG_PATTERN)
_SEPARATOR_REGEX = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True, slots=True)
class Slug:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > SLUG_MAX_LENGTH or not _SLUG_REGEX.fullmatch(self.value):
            raise ValidationError(
                f"Invalid slug: '{self.value}'", code=CommonErrorCode.INVALID_SLUG, params={"value": self.value}
            )

    @classmethod
    def from_text(cls, text: str) -> Self:
        ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        value = _SEPARATOR_REGEX.sub("-", ascii_text.lower()).strip("-")
        return cls(value[:SLUG_MAX_LENGTH].rstrip("-"))

    def __str__(self) -> str:
        return self.value
