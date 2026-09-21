from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from shared.domain.money import Money

from saury_backend.catalog.domain.entities.colorway import Colorway
from saury_backend.catalog.domain.entities.image import Image
from saury_backend.catalog.domain.entities.size_variant import SizeVariant
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerSort
from saury_backend.catalog.domain.value_objects.spec_sheet import SpecSheet
from saury_backend.catalog.domain.value_objects.testimonial import Testimonial


@dataclass(frozen=True, slots=True)
class MoneyDTO:
    amount: Decimal
    currency: str

    @classmethod
    def from_money(cls, money: Money) -> Self:
        return cls(amount=money.amount, currency=money.currency)


@dataclass(frozen=True, slots=True)
class SizeVariantDTO:
    size: Decimal
    stock: int

    @classmethod
    def from_entity(cls, variant: SizeVariant) -> Self:
        return cls(size=variant.size.value, stock=variant.stock)


@dataclass(frozen=True, slots=True)
class ColorwayDTO:
    id: UUID
    name: str
    color_code: str
    sku: str
    price_override: MoneyDTO | None
    effective_price: MoneyDTO
    sizes: list[SizeVariantDTO]

    @classmethod
    def from_entity(cls, colorway: Colorway, base_price: Money) -> Self:
        return cls(
            id=colorway.id,
            name=colorway.name,
            color_code=colorway.color_code,
            sku=colorway.sku,
            price_override=MoneyDTO.from_money(colorway.price_override) if colorway.price_override else None,
            effective_price=MoneyDTO.from_money(colorway.effective_price(base_price)),
            sizes=[SizeVariantDTO.from_entity(variant) for variant in colorway.sizes],
        )


@dataclass(frozen=True, slots=True)
class ImageDTO:
    id: UUID
    public_id: str
    url: str
    alt: str
    position: int
    is_primary: bool

    @classmethod
    def from_entity(cls, image: Image) -> Self:
        return cls(
            id=image.id,
            public_id=image.public_id,
            url=image.url,
            alt=image.alt,
            position=image.position,
            is_primary=image.is_primary,
        )


@dataclass(frozen=True, slots=True)
class SpecSheetDTO:
    material: str = ""
    technology: str = ""
    weight: str = ""
    cushioning: str = ""

    @classmethod
    def from_value(cls, specs: SpecSheet) -> Self:
        return cls(
            material=specs.material,
            technology=specs.technology,
            weight=specs.weight,
            cushioning=specs.cushioning,
        )

    def to_value(self) -> SpecSheet:
        return SpecSheet(
            material=self.material,
            technology=self.technology,
            weight=self.weight,
            cushioning=self.cushioning,
        )


@dataclass(frozen=True, slots=True)
class TestimonialDTO:
    quote: str
    author: str

    @classmethod
    def from_value(cls, testimonial: Testimonial) -> Self:
        return cls(quote=testimonial.quote, author=testimonial.author)

    def to_value(self) -> Testimonial:
        return Testimonial(quote=self.quote, author=self.author)


@dataclass(frozen=True, slots=True)
class SneakerDTO:
    id: UUID
    name: str
    slug: str
    description: str
    brand_id: UUID
    category_id: UUID
    gender: str
    base_price: MoneyDTO
    status: str
    release_date: date | None
    created_at: datetime
    updated_at: datetime
    reference: str | None
    specs: SpecSheetDTO
    usage: str
    testimonial: TestimonialDTO | None
    colorways: list[ColorwayDTO]
    images: list[ImageDTO]

    @classmethod
    def from_entity(cls, sneaker: Sneaker) -> Self:
        return cls(
            id=sneaker.id,
            name=sneaker.name,
            slug=sneaker.slug.value,
            description=sneaker.description,
            brand_id=sneaker.brand_id,
            category_id=sneaker.category_id,
            gender=sneaker.gender.value,
            base_price=MoneyDTO.from_money(sneaker.base_price),
            status=sneaker.status.value,
            release_date=sneaker.release_date,
            created_at=sneaker.created_at,
            updated_at=sneaker.updated_at,
            reference=sneaker.reference,
            specs=SpecSheetDTO.from_value(sneaker.specs),
            usage=sneaker.usage,
            testimonial=TestimonialDTO.from_value(sneaker.testimonial) if sneaker.testimonial else None,
            colorways=[ColorwayDTO.from_entity(colorway, sneaker.base_price) for colorway in sneaker.colorways],
            images=[ImageDTO.from_entity(image) for image in sneaker.images],
        )


@dataclass(frozen=True, slots=True)
class CreateSneakerCommand:
    name: str
    description: str
    brand_id: UUID
    category_id: UUID
    gender: str
    price: Decimal
    currency: str
    release_date: date | None = None
    slug: str | None = None
    reference: str | None = None
    specs: SpecSheetDTO = field(default_factory=SpecSheetDTO)
    usage: str = ""
    testimonial: TestimonialDTO | None = None


@dataclass(frozen=True, slots=True)
class UpdateSneakerCommand:
    sneaker_id: UUID
    name: str
    description: str
    brand_id: UUID
    category_id: UUID
    gender: str
    price: Decimal
    currency: str
    release_date: date | None = None
    slug: str | None = None
    reference: str | None = None
    specs: SpecSheetDTO = field(default_factory=SpecSheetDTO)
    usage: str = ""
    testimonial: TestimonialDTO | None = None


@dataclass(frozen=True, slots=True)
class ListSneakersQuery:
    brands: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    genders: tuple[str, ...] = ()
    status: str | None = None
    sizes: tuple[Decimal, ...] = ()
    colors: tuple[str, ...] = ()
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    currency: str | None = None
    in_stock: bool = False
    q: str | None = None
    sort: str = SneakerSort.CREATED_AT.value
    descending: bool = False


@dataclass(frozen=True, slots=True)
class CreateColorwayCommand:
    sneaker_id: UUID
    name: str
    color_code: str
    sku: str
    price_override: Decimal | None = None


@dataclass(frozen=True, slots=True)
class UpdateColorwayCommand:
    sneaker_id: UUID
    colorway_id: UUID
    name: str
    color_code: str
    sku: str
    price_override: Decimal | None = None


@dataclass(frozen=True, slots=True)
class SetSizeStockCommand:
    sneaker_id: UUID
    colorway_id: UUID
    size: Decimal
    stock: int


@dataclass(frozen=True, slots=True)
class RemoveSizeCommand:
    sneaker_id: UUID
    colorway_id: UUID
    size: Decimal


@dataclass(frozen=True, slots=True)
class UploadSneakerImageCommand:
    sneaker_id: UUID
    content: bytes = field(repr=False)
    filename: str
    alt: str = ""


@dataclass(frozen=True, slots=True)
class ReorderSneakerImagesCommand:
    sneaker_id: UUID
    image_ids: list[UUID]
