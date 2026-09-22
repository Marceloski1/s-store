import re
from dataclasses import dataclass

from shared.domain.errors import ValidationError

from saury_backend.identity.domain.error_codes import IdentityErrorCode

EMAIL_MAX_LENGTH = 254
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if len(normalized) > EMAIL_MAX_LENGTH or not _EMAIL_REGEX.fullmatch(normalized):
            raise ValidationError(
                f"Invalid email: '{self.value}'", code=IdentityErrorCode.INVALID_EMAIL, params={"value": self.value}
            )
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
