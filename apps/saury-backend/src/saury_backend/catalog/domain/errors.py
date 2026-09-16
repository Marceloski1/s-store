from uuid import UUID

from shared.domain.errors import ConflictError, NotFoundError, ValidationError
from shared.domain.slug import Slug

from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus


class BrandNotFound(NotFoundError):
    def __init__(self, brand_id: UUID) -> None:
        super().__init__(f"Brand '{brand_id}' not found")


class BrandSlugAlreadyExists(ConflictError):
    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Brand slug '{slug}' already exists")


class BrandInUse(ConflictError):
    def __init__(self, brand_id: UUID) -> None:
        super().__init__(f"Brand '{brand_id}' has sneakers and cannot be deleted")


class CategoryNotFound(NotFoundError):
    def __init__(self, category_id: UUID) -> None:
        super().__init__(f"Category '{category_id}' not found")


class CategorySlugAlreadyExists(ConflictError):
    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Category slug '{slug}' already exists")


class CategoryInUse(ConflictError):
    def __init__(self, category_id: UUID) -> None:
        super().__init__(f"Category '{category_id}' has sneakers and cannot be deleted")


class SneakerNotFound(NotFoundError):
    def __init__(self, sneaker_id: UUID) -> None:
        super().__init__(f"Sneaker '{sneaker_id}' not found")


class SneakerSlugAlreadyExists(ConflictError):
    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Sneaker slug '{slug}' already exists")


class SneakerNotPublishable(ConflictError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Sneaker cannot be published: {reason}")


class InvalidSneakerStatusTransition(ConflictError):
    def __init__(self, current: SneakerStatus, target: SneakerStatus) -> None:
        super().__init__(f"Sneaker cannot change status from '{current}' to '{target}'")


class ColorwayNotFound(NotFoundError):
    def __init__(self, colorway_id: UUID) -> None:
        super().__init__(f"Colorway '{colorway_id}' not found")


class SkuAlreadyExists(ConflictError):
    def __init__(self, sku: str) -> None:
        super().__init__(f"SKU '{sku}' already exists")


class SizeVariantNotFound(NotFoundError):
    def __init__(self, size: ShoeSize) -> None:
        super().__init__(f"Size '{size}' not found")


class ImageNotFound(NotFoundError):
    def __init__(self, image_id: UUID) -> None:
        super().__init__(f"Image '{image_id}' not found")


class ImageLimitExceeded(ConflictError):
    def __init__(self, limit: int) -> None:
        super().__init__(f"A sneaker can have at most {limit} images")


class CurrencyMismatch(ValidationError):
    def __init__(self, expected: str, actual: str) -> None:
        super().__init__(f"Price currency '{actual}' does not match sneaker currency '{expected}'")
