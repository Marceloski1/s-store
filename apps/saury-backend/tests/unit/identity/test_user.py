import pytest
from shared.domain.errors import ValidationError

from saury_backend.identity.domain.entities.user import User
from saury_backend.identity.domain.value_objects.email import Email
from saury_backend.identity.domain.value_objects.password import validate_password
from saury_backend.identity.domain.value_objects.role import Role


def make_user() -> User:
    return User.create(Email("Admin@Alesa.Local"), "Admin", "hash", Role.ADMIN)


def test_creates_active_user_with_normalized_email() -> None:
    user = make_user()

    assert user.email == Email("admin@alesa.local")
    assert str(user.email) == "admin@alesa.local"
    assert (user.role, user.is_active) == (Role.ADMIN, True)
    assert user.created_at == user.updated_at


@pytest.mark.parametrize("email", ["", "admin", "admin@alesa", "ad min@alesa.local", f"{'a' * 250}@a.io"])
def test_rejects_invalid_emails(email: str) -> None:
    with pytest.raises(ValidationError):
        Email(email)


@pytest.mark.parametrize("name", ["", "   ", "a" * 101])
def test_rejects_invalid_names(name: str) -> None:
    with pytest.raises(ValidationError):
        User.create(Email("admin@alesa.local"), name, "hash", Role.ADMIN)


def test_updates_touch_the_user() -> None:
    user = make_user()
    created_at = user.updated_at

    user.rename("  Eduardo  ")
    user.set_active(False)
    user.change_password_hash("new-hash")

    assert (user.name, user.is_active, user.password_hash) == ("Eduardo", False, "new-hash")
    assert user.updated_at >= created_at


@pytest.mark.parametrize("password", ["short", "a" * 129])
def test_rejects_invalid_passwords(password: str) -> None:
    with pytest.raises(ValidationError):
        validate_password(password)


def test_accepts_valid_passwords() -> None:
    assert validate_password("Password123!") == "Password123!"
