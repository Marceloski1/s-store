from datetime import UTC, datetime
from uuid import UUID

from shared.domain.pagination import Page, PageParams
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from saury_backend.identity.domain.entities.user import User
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.infrastructure.persistence.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> None:
        await self._session.merge(
            UserModel(
                id=user.id,
                email=user.email.value,
                name=user.name,
                password_hash=user.password_hash,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )

    async def get(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_entity(model) if model is not None else None

    async def get_by_email(self, email: Email) -> User | None:
        model = await self._session.scalar(select(UserModel).where(UserModel.email == email.value))
        return _to_entity(model) if model is not None else None

    async def paginate(self, params: PageParams) -> Page[User]:
        total = await self._session.scalar(select(func.count()).select_from(UserModel)) or 0
        models = await self._session.scalars(
            select(UserModel).order_by(UserModel.name, UserModel.id).offset(params.offset).limit(params.size)
        )
        return Page(items=[_to_entity(model) for model in models], total=total, page=params.page, size=params.size)

    async def delete(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if model is not None:
            await self._session.delete(model)


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=Email(model.email),
        name=model.name,
        password_hash=model.password_hash,
        role=model.role,
        is_active=model.is_active,
        created_at=_as_utc(model.created_at),
        updated_at=_as_utc(model.updated_at),
    )
