from uuid import UUID

from shared.domain.errors import ConflictError, NotFoundError, ValidationError
from shared.domain.slug import Slug

from saury_backend.catalog.domain.error_codes import CatalogErrorCode
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus


class BrandNotFound(NotFoundError):
    code = CatalogErrorCode.BRAND_NOT_FOUND

    def __init__(self, brand_id: UUID) -> None:
        super().__init__(f"Brand '{brand_id}' not found", params={"id": str(brand_id)})


class BrandSlugAlreadyExists(ConflictError):
    code = CatalogErrorCode.BRAND_SLUG_ALREADY_EXISTS

    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Brand slug '{slug}' already exists", params={"slug": slug.value})


class BrandInUse(ConflictError):
    code = CatalogErrorCode.BRAND_IN_USE

    def __init__(self, brand_id: UUID) -> None:
        super().__init__(f"Brand '{brand_id}' has sneakers and cannot be deleted", params={"id": str(brand_id)})


class CategoryNotFound(NotFoundError):
    code = CatalogErrorCode.CATEGORY_NOT_FOUND

    def __init__(self, category_id: UUID) -> None:
        super().__init__(f"Category '{category_id}' not found", params={"id": str(category_id)})


class CategorySlugAlreadyExists(ConflictError):
    code = CatalogErrorCode.CATEGORY_SLUG_ALREADY_EXISTS

    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Category slug '{slug}' already exists", params={"slug": slug.value})


class CategoryInUse(ConflictError):
    code = CatalogErrorCode.CATEGORY_IN_USE

    def __init__(self, category_id: UUID) -> None:
        super().__init__(
            f"Category '{category_id}' has sneakers and cannot be deleted", params={"id": str(category_id)}
        )


class SneakerNotFound(NotFoundError):
    code = CatalogErrorCode.SNEAKER_NOT_FOUND

    def __init__(self, sneaker_id: UUID) -> None:
        super().__init__(f"Sneaker '{sneaker_id}' not found", params={"id": str(sneaker_id)})


class SneakerSlugAlreadyExists(ConflictError):
    code = CatalogErrorCode.SNEAKER_SLUG_ALREADY_EXISTS

    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Sneaker slug '{slug}' already exists", params={"slug": slug.value})


class SneakerSlugNotFound(NotFoundError):
    code = CatalogErrorCode.SNEAKER_NOT_FOUND

    def __init__(self, slug: Slug) -> None:
        super().__init__(f"Sneaker '{slug}' not found", params={"slug": slug.value})


class SneakerReferenceAlreadyExists(ConflictError):
    code = CatalogErrorCode.SNEAKER_REFERENCE_ALREADY_EXISTS

    def __init__(self, reference: str) -> None:
        super().__init__(f"Sneaker reference '{reference}' already exists", params={"reference": reference})


class SneakerNotPublishable(ConflictError):
    pass


class SneakerNeedsPrimaryImage(SneakerNotPublishable):
    code = CatalogErrorCode.SNEAKER_NEEDS_PRIMARY_IMAGE

    def __init__(self) -> None:
        super().__init__("Sneaker cannot be published: it needs a primary image")


class SneakerNeedsSizedColorway(SneakerNotPublishable):
    code = CatalogErrorCode.SNEAKER_NEEDS_SIZED_COLORWAY

    def __init__(self) -> None:
        super().__init__("Sneaker cannot be published: it needs at least one colorway with a size")


class InvalidSneakerStatusTransition(ConflictError):
    code = CatalogErrorCode.INVALID_STATUS_TRANSITION

    def __init__(self, current: SneakerStatus, target: SneakerStatus) -> None:
        super().__init__(
            f"Sneaker cannot change status from '{current}' to '{target}'",
            params={"from": current.value, "to": target.value},
        )


class ColorwayNotFound(NotFoundError):
    code = CatalogErrorCode.COLORWAY_NOT_FOUND

    def __init__(self, colorway_id: UUID) -> None:
        super().__init__(f"Colorway '{colorway_id}' not found", params={"id": str(colorway_id)})


class SkuAlreadyExists(ConflictError):
    code = CatalogErrorCode.SKU_ALREADY_EXISTS

    def __init__(self, sku: str) -> None:
        super().__init__(f"SKU '{sku}' already exists", params={"sku": sku})


class SizeVariantNotFound(NotFoundError):
    code = CatalogErrorCode.SIZE_NOT_FOUND

    def __init__(self, size: ShoeSize) -> None:
        super().__init__(f"Size '{size}' not found", params={"size": str(size)})


class ImageNotFound(NotFoundError):
    code = CatalogErrorCode.IMAGE_NOT_FOUND

    def __init__(self, image_id: UUID) -> None:
        super().__init__(f"Image '{image_id}' not found", params={"id": str(image_id)})


class ImageLimitExceeded(ConflictError):
    code = CatalogErrorCode.IMAGE_LIMIT_EXCEEDED

    def __init__(self, limit: int) -> None:
        super().__init__(f"A sneaker can have at most {limit} images", params={"limit": limit})


class InvalidImage(ValidationError):
    code = CatalogErrorCode.IMAGE_INVALID

    def __init__(self, message: str, reason: str) -> None:
        super().__init__(message, params={"reason": reason})


class CurrencyMismatch(ValidationError):
    code = CatalogErrorCode.CURRENCY_MISMATCH

    def __init__(self, expected: str, actual: str) -> None:
        super().__init__(
            f"Price currency '{actual}' does not match sneaker currency '{expected}'",
            params={"expected": expected, "actual": actual},
        )
