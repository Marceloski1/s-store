import argparse
import asyncio
import getpass
import os
import sys

from shared.domain.errors import DomainError
from shared.infrastructure.persistence.database import create_engine, create_session_factory
from shared.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork

from saury_backend.config.settings import get_settings
from saury_backend.identity.application.dtos.user import CreateUserCommand, UserDTO
from saury_backend.identity.application.use_cases.user import CreateSuperAdmin
from saury_backend.identity.infrastructure.persistence.user_repository import SqlAlchemyUserRepository
from saury_backend.identity.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher

PASSWORD_ENV_VAR = "SUPER_ADMIN_PASSWORD"


def _read_password() -> str:
    password = os.environ.get(PASSWORD_ENV_VAR)
    if password:
        return password
    password = getpass.getpass("Password: ")
    if password != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords do not match")
    return password


async def create_super_admin(database_url: str, command: CreateUserCommand) -> UserDTO:
    engine = create_engine(database_url)
    try:
        async with create_session_factory(engine)() as session:
            use_case = CreateSuperAdmin(
                SqlAlchemyUserRepository(session), Argon2PasswordHasher(), SqlAlchemyUnitOfWork(session)
            )
            return await use_case.execute(command)
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(prog="create-super-admin", description="Create the first SUPER_ADMIN user")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    arguments = parser.parse_args()
    command = CreateUserCommand(email=arguments.email, name=arguments.name, password=_read_password())
    try:
        user = asyncio.run(create_super_admin(get_settings().async_database_url, command))
    except DomainError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print(f"SUPER_ADMIN created: {user.email} ({user.id})")
