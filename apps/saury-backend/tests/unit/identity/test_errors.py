from uuid import uuid7

import pytest
from shared.domain.errors import ValidationError

from saury_backend.identity.domain.error_codes import CannotManageUserReason, IdentityErrorCode
from saury_backend.identity.domain.errors import CannotManageUser, InsufficientRole, UserNotFound
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.password import validate_password
from saury_backend.identity.domain.value_objects.role import Role


def test_identity_errors_expose_codes_and_params() -> None:
    user_id = uuid7()

    assert (UserNotFound(user_id).code, UserNotFound(user_id).params) == (
        IdentityErrorCode.USER_NOT_FOUND,
        {"id": str(user_id)},
    )
    assert InsufficientRole(Role.SUPER_ADMIN).params == {"role": "SUPER_ADMIN"}
    assert CannotManageUser(CannotManageUserReason.SELF).params == {"reason": "SELF"}
    assert CannotManageUser(CannotManageUserReason.SUPER_ADMIN).code == IdentityErrorCode.CANNOT_MANAGE_USER


@pytest.mark.parametrize(
    ("action", "code", "params"),
    [
        (lambda: Email("not-an-email"), IdentityErrorCode.INVALID_EMAIL, {"value": "not-an-email"}),
        (lambda: validate_password("short"), IdentityErrorCode.PASSWORD_TOO_SHORT, {"min": 8}),
        (lambda: validate_password("a" * 129), IdentityErrorCode.PASSWORD_TOO_LONG, {"max": 128}),
    ],
    ids=["email", "password-short", "password-long"],
)
def test_identity_validations_raise_coded_errors(action, code: IdentityErrorCode, params: dict[str, object]) -> None:
    with pytest.raises(ValidationError) as raised:
        action()

    assert (raised.value.code, raised.value.params) == (code, params)
