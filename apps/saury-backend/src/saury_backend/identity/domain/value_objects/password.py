from shared.domain.errors import ValidationError

from saury_backend.identity.domain.error_codes import IdentityErrorCode

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def validate_password(password: str) -> str:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationError(
            f"password must be at least {PASSWORD_MIN_LENGTH} characters",
            code=IdentityErrorCode.PASSWORD_TOO_SHORT,
            params={"min": PASSWORD_MIN_LENGTH},
        )
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValidationError(
            f"password must be at most {PASSWORD_MAX_LENGTH} characters",
            code=IdentityErrorCode.PASSWORD_TOO_LONG,
            params={"max": PASSWORD_MAX_LENGTH},
        )
    return password
