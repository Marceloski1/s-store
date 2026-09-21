from uuid import uuid7

import pytest
from shared.domain.errors import ValidationError
from shared.domain.pagination import PageParams

from saury_backend.identity.application.dtos.user import CreateUserCommand, UpdateAdminUserCommand
from saury_backend.identity.application.use_cases.user import (
    CreateAdminUser,
    CreateSuperAdmin,
    DeleteAdminUser,
    ListUsers,
    UpdateAdminUser,
)
from saury_backend.identity.domain.errors import CannotManageUser, EmailAlreadyExists, UserNotFound
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.role import Role
from support.identity_fakes import store_user


def create_command(email: str = "new@alesa.local", password: str = "Password123!") -> CreateUserCommand:
    return CreateUserCommand(email=email, name="Nuevo Admin", password=password)


async def test_create_admin_user_hashes_the_password(user_repository, hasher, unit_of_work) -> None:
    created = await CreateAdminUser(user_repository, hasher, unit_of_work).execute(create_command("New@Alesa.local"))

    stored = await user_repository.get_by_email(Email("new@alesa.local"))
    assert (created.email, created.role, created.is_active) == ("new@alesa.local", "ADMIN", True)
    assert stored is not None and stored.password_hash == "hashed:Password123!"
    assert unit_of_work.commits == 1


async def test_create_super_admin_uses_its_role(user_repository, hasher, unit_of_work) -> None:
    created = await CreateSuperAdmin(user_repository, hasher, unit_of_work).execute(create_command())

    assert created.role == "SUPER_ADMIN"


async def test_create_user_rejects_duplicated_emails(user_repository, hasher, unit_of_work) -> None:
    await store_user(user_repository, "new@alesa.local")

    with pytest.raises(EmailAlreadyExists):
        await CreateAdminUser(user_repository, hasher, unit_of_work).execute(create_command("NEW@alesa.local"))


async def test_create_user_rejects_weak_passwords(user_repository, hasher, unit_of_work) -> None:
    with pytest.raises(ValidationError):
        await CreateAdminUser(user_repository, hasher, unit_of_work).execute(create_command(password="short"))


async def test_list_users_pages_by_name(user_repository) -> None:
    for email in ("carla@alesa.local", "ana@alesa.local", "beto@alesa.local"):
        await store_user(user_repository, email)

    page = await ListUsers(user_repository).execute(PageParams(page=1, size=2))

    assert [user.name for user in page.items] == ["ana", "beto"]
    assert page.total == 3


async def test_update_admin_user_changes_name_status_and_password(user_repository, hasher, unit_of_work) -> None:
    admin = await store_user(user_repository, "admin@alesa.local")

    updated = await UpdateAdminUser(user_repository, hasher, unit_of_work).execute(
        UpdateAdminUserCommand(user_id=admin.id, name="Eduardo", is_active=False, password="NewPassword1!")
    )

    stored = await user_repository.get(admin.id)
    assert (updated.name, updated.is_active) == ("Eduardo", False)
    assert stored is not None and stored.password_hash == "hashed:NewPassword1!"


async def test_update_admin_user_keeps_omitted_fields(user_repository, hasher, unit_of_work) -> None:
    admin = await store_user(user_repository, "admin@alesa.local")

    updated = await UpdateAdminUser(user_repository, hasher, unit_of_work).execute(
        UpdateAdminUserCommand(user_id=admin.id)
    )

    assert (updated.name, updated.is_active) == ("admin", True)


async def test_super_admins_cannot_be_managed(user_repository, hasher, unit_of_work) -> None:
    super_admin = await store_user(user_repository, "super@alesa.local", Role.SUPER_ADMIN)
    other = await store_user(user_repository, "other@alesa.local", Role.SUPER_ADMIN)

    with pytest.raises(CannotManageUser):
        await UpdateAdminUser(user_repository, hasher, unit_of_work).execute(
            UpdateAdminUserCommand(user_id=super_admin.id, is_active=False)
        )
    with pytest.raises(CannotManageUser):
        await DeleteAdminUser(user_repository, unit_of_work).execute(super_admin.id, acting_user_id=other.id)


async def test_missing_users_are_not_found(user_repository, hasher, unit_of_work) -> None:
    with pytest.raises(UserNotFound):
        await UpdateAdminUser(user_repository, hasher, unit_of_work).execute(UpdateAdminUserCommand(user_id=uuid7()))
    with pytest.raises(UserNotFound):
        await DeleteAdminUser(user_repository, unit_of_work).execute(uuid7(), acting_user_id=uuid7())


async def test_delete_admin_user(user_repository, unit_of_work) -> None:
    super_admin = await store_user(user_repository, "super@alesa.local", Role.SUPER_ADMIN)
    admin = await store_user(user_repository, "admin@alesa.local")

    await DeleteAdminUser(user_repository, unit_of_work).execute(admin.id, acting_user_id=super_admin.id)

    assert await user_repository.get(admin.id) is None
    assert unit_of_work.commits == 1


async def test_users_cannot_delete_themselves(user_repository, unit_of_work) -> None:
    super_admin = await store_user(user_repository, "super@alesa.local", Role.SUPER_ADMIN)

    with pytest.raises(CannotManageUser):
        await DeleteAdminUser(user_repository, unit_of_work).execute(super_admin.id, acting_user_id=super_admin.id)
