from dataclasses import dataclass

from shared.domain.errors import ValidationError

SPEC_FIELD_MAX_LENGTH = 100


def _clean_spec(value: str, field: str) -> str:
    cleaned = value.strip()
    if len(cleaned) > SPEC_FIELD_MAX_LENGTH:
        raise ValidationError(f"{field} must be at most {SPEC_FIELD_MAX_LENGTH} characters")
    return cleaned


@dataclass(frozen=True, slots=True)
class SpecSheet:
    material: str = ""
    technology: str = ""
    weight: str = ""
    cushioning: str = ""

    def __post_init__(self) -> None:
        for field in ("material", "technology", "weight", "cushioning"):
            object.__setattr__(self, field, _clean_spec(getattr(self, field), field))
