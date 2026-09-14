from shared.domain.errors import ValidationError


def require_text(value: str, *, field: str, max_length: int) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field} must not be empty")
    if len(cleaned) > max_length:
        raise ValidationError(f"{field} must be at most {max_length} characters")
    return cleaned
