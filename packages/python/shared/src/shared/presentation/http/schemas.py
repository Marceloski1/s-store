from typing import Annotated, Self

from fastapi import status
from pydantic import BaseModel, StringConstraints

from shared.domain.pagination import Page
from shared.domain.slug import SLUG_MAX_LENGTH, SLUG_PATTERN

SlugStr = Annotated[str, StringConstraints(pattern=SLUG_PATTERN, max_length=SLUG_MAX_LENGTH)]


class PageResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def from_page(cls, page: Page[T]) -> Self:
        return cls(items=page.items, total=page.total, page=page.page, size=page.size, pages=page.pages)


class ErrorResponse(BaseModel):
    detail: str


NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}
CONFLICT_RESPONSE = {status.HTTP_409_CONFLICT: {"model": ErrorResponse}}
UNPROCESSABLE_RESPONSE = {status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse}}
