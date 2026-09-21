import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Self
from uuid import UUID, uuid7

from shared.domain.errors import ValidationError
from shared.domain.money import Money
from shared.domain.slug import Slug
from shared.domain.validation import require_text

from saury_backend.catalog.domain.entities.colorway import SKU_PATTERN, Colorway, normalize_sku
from saury_backend.catalog.domain.entities.image import Image
from saury_backend.catalog.domain.entities.size_variant import SizeVariant
from saury_backend.catalog.domain.errors import (
    ColorwayNotFound,
    CurrencyMismatch,
    ImageLimitExceeded,
    ImageNotFound,
    InvalidSneakerStatusTransition,
    SkuAlreadyExists,
    SneakerNotPublishable,
)
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus
from saury_backend.catalog.domain.value_objects.spec_sheet import SpecSheet
from saury_backend.catalog.domain.value_objects.testimonial import Testimonial

SNEAKER_NAME_MAX_LENGTH = 150
SNEAKER_DESCRIPTION_MAX_LENGTH = 2000
SNEAKER_USAGE_MAX_LENGTH = 500
SNEAKER_REFERENCE_MAX_LENGTH = 64
MAX_IMAGES_PER_SNEAKER = 8

_REFERENCE_REGEX = re.compile(SKU_PATTERN)

_ALLOWED_TRANSITIONS = {
    (SneakerStatus.DRAFT, SneakerStatus.ACTIVE),
    (SneakerStatus.ACTIVE, SneakerStatus.ARCHIVED),
    (SneakerStatus.ARCHIVED, SneakerStatus.DRAFT),
}


def _now() -> datetime:
    return datetime.now(UTC)


def _clean_description(description: str) -> str:
    cleaned = description.strip()
    if len(cleaned) > SNEAKER_DESCRIPTION_MAX_LENGTH:
        raise ValidationError(f"description must be at most {SNEAKER_DESCRIPTION_MAX_LENGTH} characters")
    return cleaned


def _clean_usage(usage: str) -> str:
    cleaned = usage.strip()
    if len(cleaned) > SNEAKER_USAGE_MAX_LENGTH:
        raise ValidationError(f"usage must be at most {SNEAKER_USAGE_MAX_LENGTH} characters")
    return cleaned


def normalize_reference(reference: str | None) -> str | None:
    if reference is None or not reference.strip():
        return None
    value = reference.strip().upper()
    if len(value) > SNEAKER_REFERENCE_MAX_LENGTH or not _REFERENCE_REGEX.fullmatch(value):
        raise ValidationError(f"Invalid reference: '{reference}'")
    return value


@dataclass(slots=True)
class Sneaker:
    id: UUID
    name: str
    slug: Slug
    description: str
    brand_id: UUID
    category_id: UUID
    gender: Gender
    base_price: Money
    status: SneakerStatus
    release_date: date | None
    created_at: datetime
    updated_at: datetime
    reference: str | None = None
    specs: SpecSheet = field(default_factory=SpecSheet)
    usage: str = ""
    testimonial: Testimonial | None = None
    colorways: list[Colorway] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = require_text(self.name, field="name", max_length=SNEAKER_NAME_MAX_LENGTH)
        self.description = _clean_description(self.description)
        self.reference = normalize_reference(self.reference)
        self.usage = _clean_usage(self.usage)
        self.colorways.sort(key=lambda colorway: colorway.name)
        self.images.sort(key=lambda image: image.position)

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        brand_id: UUID,
        category_id: UUID,
        gender: Gender,
        base_price: Money,
        release_date: date | None = None,
        slug: Slug | None = None,
        reference: str | None = None,
        specs: SpecSheet | None = None,
        usage: str = "",
        testimonial: Testimonial | None = None,
    ) -> Self:
        clean_name = require_text(name, field="name", max_length=SNEAKER_NAME_MAX_LENGTH)
        now = _now()
        return cls(
            id=uuid7(),
            name=clean_name,
            slug=slug or Slug.from_text(clean_name),
            description=description,
            brand_id=brand_id,
            category_id=category_id,
            gender=gender,
            base_price=base_price,
            status=SneakerStatus.DRAFT,
            release_date=release_date,
            created_at=now,
            updated_at=now,
            reference=reference,
            specs=specs or SpecSheet(),
            usage=usage,
            testimonial=testimonial,
        )

    def update(
        self,
        name: str,
        description: str,
        brand_id: UUID,
        category_id: UUID,
        gender: Gender,
        base_price: Money,
        release_date: date | None = None,
        slug: Slug | None = None,
        reference: str | None = None,
        specs: SpecSheet | None = None,
        usage: str = "",
        testimonial: Testimonial | None = None,
    ) -> None:
        for colorway in self.colorways:
            if colorway.price_override is not None and colorway.price_override.currency != base_price.currency:
                raise CurrencyMismatch(expected=colorway.price_override.currency, actual=base_price.currency)
        self.name = require_text(name, field="name", max_length=SNEAKER_NAME_MAX_LENGTH)
        self.slug = slug or Slug.from_text(self.name)
        self.description = _clean_description(description)
        self.brand_id = brand_id
        self.category_id = category_id
        self.gender = gender
        self.base_price = base_price
        self.release_date = release_date
        self.reference = normalize_reference(reference)
        self.specs = specs or SpecSheet()
        self.usage = _clean_usage(usage)
        self.testimonial = testimonial
        self._touch()

    def add_colorway(self, name: str, color_code: str, sku: str, price_override: Money | None = None) -> Colorway:
        self._ensure_price_currency(price_override)
        self._ensure_sku_is_unique(sku)
        colorway = Colorway.create(name, color_code, sku, price_override)
        self.colorways.append(colorway)
        self.colorways.sort(key=lambda item: item.name)
        self._touch()
        return colorway

    def update_colorway(
        self, colorway_id: UUID, name: str, color_code: str, sku: str, price_override: Money | None
    ) -> Colorway:
        colorway = self.get_colorway(colorway_id)
        self._ensure_price_currency(price_override)
        self._ensure_sku_is_unique(sku, excluding=colorway_id)
        colorway.update(name, color_code, sku, price_override)
        self.colorways.sort(key=lambda item: item.name)
        self._touch()
        return colorway

    def remove_colorway(self, colorway_id: UUID) -> None:
        self.colorways.remove(self.get_colorway(colorway_id))
        self._touch()

    def get_colorway(self, colorway_id: UUID) -> Colorway:
        colorway = next((item for item in self.colorways if item.id == colorway_id), None)
        if colorway is None:
            raise ColorwayNotFound(colorway_id)
        return colorway

    def set_size_stock(self, colorway_id: UUID, size: ShoeSize, stock: int) -> SizeVariant:
        variant = self.get_colorway(colorway_id).set_stock(size, stock)
        self._touch()
        return variant

    def remove_size(self, colorway_id: UUID, size: ShoeSize) -> None:
        self.get_colorway(colorway_id).remove_size(size)
        self._touch()

    def add_image(self, public_id: str, url: str, alt: str = "") -> Image:
        if len(self.images) >= MAX_IMAGES_PER_SNEAKER:
            raise ImageLimitExceeded(MAX_IMAGES_PER_SNEAKER)
        image = Image.create(public_id, url, alt, position=len(self.images))
        image.is_primary = not self.images
        self.images.append(image)
        self._touch()
        return image

    def remove_image(self, image_id: UUID) -> Image:
        image = self.get_image(image_id)
        self.images.remove(image)
        self._renumber_images()
        if image.is_primary and self.images:
            self.images[0].is_primary = True
        self._touch()
        return image

    def reorder_images(self, image_ids: list[UUID]) -> None:
        if len(image_ids) != len(self.images) or set(image_ids) != {image.id for image in self.images}:
            raise ValidationError("Image order must contain every image of the sneaker exactly once")
        by_id = {image.id: image for image in self.images}
        self.images = [by_id[image_id] for image_id in image_ids]
        self._renumber_images()
        self._touch()

    def mark_primary_image(self, image_id: UUID) -> Image:
        primary = self.get_image(image_id)
        for image in self.images:
            image.is_primary = image is primary
        self._touch()
        return primary

    def get_image(self, image_id: UUID) -> Image:
        image = next((item for item in self.images if item.id == image_id), None)
        if image is None:
            raise ImageNotFound(image_id)
        return image

    @property
    def primary_image(self) -> Image | None:
        return next((image for image in self.images if image.is_primary), None)

    def publish(self) -> None:
        self._ensure_transition(SneakerStatus.ACTIVE)
        if self.primary_image is None:
            raise SneakerNotPublishable("it needs a primary image")
        if not any(colorway.has_sizes for colorway in self.colorways):
            raise SneakerNotPublishable("it needs at least one colorway with a size")
        self._change_status(SneakerStatus.ACTIVE)

    def archive(self) -> None:
        self._ensure_transition(SneakerStatus.ARCHIVED)
        self._change_status(SneakerStatus.ARCHIVED)

    def unarchive(self) -> None:
        self._ensure_transition(SneakerStatus.DRAFT)
        self._change_status(SneakerStatus.DRAFT)

    def _ensure_transition(self, target: SneakerStatus) -> None:
        if (self.status, target) not in _ALLOWED_TRANSITIONS:
            raise InvalidSneakerStatusTransition(self.status, target)

    def _change_status(self, target: SneakerStatus) -> None:
        self.status = target
        self._touch()

    def _ensure_price_currency(self, price: Money | None) -> None:
        if price is not None and price.currency != self.base_price.currency:
            raise CurrencyMismatch(expected=self.base_price.currency, actual=price.currency)

    def _ensure_sku_is_unique(self, sku: str, excluding: UUID | None = None) -> None:
        normalized = normalize_sku(sku)
        if any(colorway.sku == normalized and colorway.id != excluding for colorway in self.colorways):
            raise SkuAlreadyExists(normalized)

    def _renumber_images(self) -> None:
        for position, image in enumerate(self.images):
            image.position = position

    def _touch(self) -> None:
        self.updated_at = _now()
