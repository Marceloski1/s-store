from datetime import datetime
from uuid import UUID

from shared.infrastructure.persistence.database import Base
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from saury_backend.identity.domain.entities.user import USER_NAME_MAX_LENGTH
from saury_backend.identity.domain.value_objects.email import EMAIL_MAX_LENGTH
from saury_backend.identity.domain.value_objects.role import Role

PASSWORD_HASH_MAX_LENGTH = 255


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), unique=True)
    name: Mapped[str] = mapped_column(String(USER_NAME_MAX_LENGTH))
    password_hash: Mapped[str] = mapped_column(String(PASSWORD_HASH_MAX_LENGTH))
    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            name="role",
            native_enum=False,
            create_constraint=True,
            length=max(len(member.value) for member in Role),
            values_callable=lambda members: [member.value for member in members],
        )
    )
    is_active: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
