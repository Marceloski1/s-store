from uuid import UUID

from shared.domain.errors import ConflictError, NotFoundError
from shared.domain.slug import Slug


class BrandNotFound(NotFoundError):
    def __init__(self, brand_id: UUID) -> None:
        super().__init__(f"Brand '{brand_id}' not found")


class BrandSlugAlreadyExists(ConflictError):
    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Brand slug '{slug}' already exists")


class CategoryNotFound(NotFoundError):
    def __init__(self, category_id: UUID) -> None:
        super().__init__(f"Category '{category_id}' not found")


class CategorySlugAlreadyExists(ConflictError):
    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Category slug '{slug}' already exists")
