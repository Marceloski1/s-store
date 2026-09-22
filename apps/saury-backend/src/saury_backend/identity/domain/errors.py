from uuid import UUID

from shared.domain.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError

from saury_backend.identity.domain.error_codes import CannotManageUserReason, IdentityErrorCode
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.role import Role

_CANNOT_MANAGE_MESSAGES = {
    CannotManageUserReason.SUPER_ADMIN: "only ADMIN users can be managed",
    CannotManageUserReason.SELF: "you cannot delete yourself",
}


class UserNotFound(NotFoundError):
    code = IdentityErrorCode.USER_NOT_FOUND

    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"User '{user_id}' not found", params={"id": str(user_id)})


class EmailAlreadyExists(ConflictError):
    code = IdentityErrorCode.EMAIL_ALREADY_EXISTS

    def __init__(self, email: Email) -> None:
        super().__init__(f"Email '{email}' is already registered", params={"email": email.value})


class InvalidCredentials(UnauthorizedError):
    code = IdentityErrorCode.INVALID_CREDENTIALS

    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InactiveUser(UnauthorizedError):
    code = IdentityErrorCode.INACTIVE_USER

    def __init__(self) -> None:
        super().__init__("User is inactive")


class NotAuthenticated(UnauthorizedError):
    code = IdentityErrorCode.NOT_AUTHENTICATED

    def __init__(self) -> None:
        super().__init__("Not authenticated")


class InsufficientRole(ForbiddenError):
    code = IdentityErrorCode.INSUFFICIENT_ROLE

    def __init__(self, required: Role) -> None:
        super().__init__(f"This action requires the {required} role", params={"role": required.value})


class CannotManageUser(ConflictError):
    code = IdentityErrorCode.CANNOT_MANAGE_USER

    def __init__(self, reason: CannotManageUserReason) -> None:
        super().__init__(
            f"User cannot be managed: {_CANNOT_MANAGE_MESSAGES[reason]}", params={"reason": reason.value}
        )
