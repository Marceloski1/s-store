import pytest

from shared.domain.errors import ValidationError
from shared.domain.slug import SLUG_MAX_LENGTH, Slug


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Air Jordan 1", "air-jordan-1"),
        ("  Nike   SB  ", "nike-sb"),
        ("Café Crème", "cafe-creme"),
        ("On/Running", "on-running"),
    ],
)
def test_from_text_normalizes_text(text: str, expected: str) -> None:
    assert Slug.from_text(text).value == expected


def test_from_text_truncates_to_max_length() -> None:
    assert len(Slug.from_text("a" * (SLUG_MAX_LENGTH + 10)).value) == SLUG_MAX_LENGTH


@pytest.mark.parametrize("value", ["", "Nike", "nike--sb", "-nike", "nike_sb", "a" * (SLUG_MAX_LENGTH + 1)])
def test_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValidationError):
        Slug(value)


def test_from_text_rejects_text_without_valid_characters() -> None:
    with pytest.raises(ValidationError):
        Slug.from_text("!!!")
