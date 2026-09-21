from fastapi.testclient import TestClient
from shared.infrastructure.persistence.database import create_engine, create_session_factory

from saury_backend.identity.domain.entities.user import User
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.role import Role
from saury_backend.identity.infrastructure.persistence.user_repository import SqlAlchemyUserRepository
from saury_backend.identity.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher

ADMIN_EMAIL = "admin@test.local"
SUPER_ADMIN_EMAIL = "super@test.local"
PASSWORD = "Password123!"


async def seed_user(
    database_url: str, email: str, role: Role, *, password: str = PASSWORD, is_active: bool = True
) -> User:
    user = User.create(Email(email), email.split("@")[0], Argon2PasswordHasher().hash(password), role)
    user.is_active = is_active
    engine = create_engine(database_url)
    async with create_session_factory(engine)() as session:
        await SqlAlchemyUserRepository(session).save(user)
        await session.commit()
    await engine.dispose()
    return user


def login(client: TestClient, email: str, password: str = PASSWORD) -> None:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
