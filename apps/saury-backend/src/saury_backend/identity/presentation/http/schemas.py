from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

from saury_backend.identity.domain.entities.user import USER_NAME_MAX_LENGTH
from saury_backend.identity.domain.value_objects.email import EMAIL_MAX_LENGTH
from saury_backend.identity.domain.value_objects.password import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
from saury_backend.identity.domain.value_objects.role import Role

EmailStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=EMAIL_MAX_LENGTH)]
NameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=USER_NAME_MAX_LENGTH)]
PasswordStr = Annotated[str, StringConstraints(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)]


class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=1, max_length=PASSWORD_MAX_LENGTH)]


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: NameStr
    password: PasswordStr


class UpdateUserRequest(BaseModel):
    name: NameStr | None = None
    is_active: bool | None = None
    password: PasswordStr | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime
