from uuid import UUID

from shared.domain.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError

from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.role import Role


class UserNotFound(NotFoundError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"User '{user_id}' not found")


class EmailAlreadyExists(ConflictError):
    def __init__(self, email: Email) -> None:
        super().__init__(f"Email '{email}' is already registered")


class InvalidCredentials(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InactiveUser(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("User is inactive")


class NotAuthenticated(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Not authenticated")


class InsufficientRole(ForbiddenError):
    def __init__(self, required: Role) -> None:
        super().__init__(f"This action requires the {required} role")


class CannotManageUser(ConflictError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"User cannot be managed: {reason}")
