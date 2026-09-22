from collections.abc import Callable
from dataclasses import dataclass

from shared.domain.errors import CommonErrorCode, ValidationError

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@dataclass(frozen=True, slots=True)
class PageParams:
    page: int = 1
    size: int = DEFAULT_PAGE_SIZE

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValidationError("page must be greater than or equal to 1", code=CommonErrorCode.INVALID_PAGE)
        if not 1 <= self.size <= MAX_PAGE_SIZE:
            raise ValidationError(
                f"size must be between 1 and {MAX_PAGE_SIZE}",
                code=CommonErrorCode.INVALID_PAGE_SIZE,
                params={"max": MAX_PAGE_SIZE},
            )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


@dataclass(frozen=True, slots=True)
class Page[T]:
    items: list[T]
    total: int
    page: int
    size: int

    @property
    def pages(self) -> int:
        return (self.total + self.size - 1) // self.size

    def map[R](self, transform: Callable[[T], R]) -> Page[R]:
        return Page(
            items=[transform(item) for item in self.items],
            total=self.total,
            page=self.page,
            size=self.size,
        )
