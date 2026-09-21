from uuid import UUID

from shared.application.unit_of_work import UnitOfWork
from shared.domain.pagination import Page, PageParams

from saury_backend.identity.application.dtos.user import CreateUserCommand, UpdateAdminUserCommand, UserDTO
from saury_backend.identity.application.ports.password_hasher import PasswordHasher
from saury_backend.identity.domain.entities.user import User
from saury_backend.identity.domain.errors import CannotManageUser, EmailAlreadyExists, UserNotFound
from saury_backend.identity.domain.repositories.user_repository import UserRepository
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.password import validate_password
from saury_backend.identity.domain.value_objects.role import Role


async def _get_user(repository: UserRepository, user_id: UUID) -> User:
    user = await repository.get(user_id)
    if user is None:
        raise UserNotFound(user_id)
    return user


async def _get_admin(repository: UserRepository, user_id: UUID) -> User:
    user = await _get_user(repository, user_id)
    if user.role is not Role.ADMIN:
        raise CannotManageUser("only ADMIN users can be managed")
    return user


class _UserCreator:
    _role: Role

    def __init__(self, repository: UserRepository, hasher: PasswordHasher, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._hasher = hasher
        self._unit_of_work = unit_of_work

    async def execute(self, command: CreateUserCommand) -> UserDTO:
        email = Email(command.email)
        password = validate_password(command.password)
        if await self._repository.get_by_email(email) is not None:
            raise EmailAlreadyExists(email)
        user = User.create(email, command.name, self._hasher.hash(password), self._role)
        await self._repository.save(user)
        await self._unit_of_work.commit()
        return UserDTO.from_entity(user)


class CreateAdminUser(_UserCreator):
    _role = Role.ADMIN


class CreateSuperAdmin(_UserCreator):
    _role = Role.SUPER_ADMIN


class ListUsers:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, params: PageParams) -> Page[UserDTO]:
        page = await self._repository.paginate(params)
        return page.map(UserDTO.from_entity)


class UpdateAdminUser:
    def __init__(self, repository: UserRepository, hasher: PasswordHasher, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._hasher = hasher
        self._unit_of_work = unit_of_work

    async def execute(self, command: UpdateAdminUserCommand) -> UserDTO:
        user = await _get_admin(self._repository, command.user_id)
        if command.name is not None:
            user.rename(command.name)
        if command.is_active is not None:
            user.set_active(command.is_active)
        if command.password is not None:
            user.change_password_hash(self._hasher.hash(validate_password(command.password)))
        await self._repository.save(user)
        await self._unit_of_work.commit()
        return UserDTO.from_entity(user)


class DeleteAdminUser:
    def __init__(self, repository: UserRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, user_id: UUID, acting_user_id: UUID) -> None:
        if user_id == acting_user_id:
            raise CannotManageUser("you cannot delete yourself")
        user = await _get_admin(self._repository, user_id)
        await self._repository.delete(user)
        await self._unit_of_work.commit()
