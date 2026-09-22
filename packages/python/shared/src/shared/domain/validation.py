from shared.domain.errors import CommonErrorCode, ValidationError


def require_text(value: str, *, field: str, max_length: int) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(
            f"{field} must not be empty", code=CommonErrorCode.TEXT_REQUIRED, params={"field": field}
        )
    if len(cleaned) > max_length:
        raise ValidationError(
            f"{field} must be at most {max_length} characters",
            code=CommonErrorCode.TEXT_TOO_LONG,
            params={"field": field, "max": max_length},
        )
    return cleaned
