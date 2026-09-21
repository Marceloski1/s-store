from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from shared.domain.slug import SLUG_MAX_LENGTH
from shared.infrastructure.persistence.database import Base
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from saury_backend.catalog.domain.entities.brand import BRAND_NAME_MAX_LENGTH
from saury_backend.catalog.domain.entities.category import CATEGORY_NAME_MAX_LENGTH
from saury_backend.catalog.domain.entities.colorway import COLORWAY_NAME_MAX_LENGTH, SKU_MAX_LENGTH
from saury_backend.catalog.domain.entities.image import (
    IMAGE_ALT_MAX_LENGTH,
    IMAGE_PUBLIC_ID_MAX_LENGTH,
    IMAGE_URL_MAX_LENGTH,
)
from saury_backend.catalog.domain.entities.sneaker import (
    SNEAKER_DESCRIPTION_MAX_LENGTH,
    SNEAKER_NAME_MAX_LENGTH,
    SNEAKER_REFERENCE_MAX_LENGTH,
    SNEAKER_USAGE_MAX_LENGTH,
)
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus
from saury_backend.catalog.domain.value_objects.spec_sheet import SPEC_FIELD_MAX_LENGTH
from saury_backend.catalog.domain.value_objects.testimonial import (
    TESTIMONIAL_AUTHOR_MAX_LENGTH,
    TESTIMONIAL_QUOTE_MAX_LENGTH,
)

PRICE_TYPE = Numeric(10, 2, asdecimal=True)
SIZE_TYPE = Numeric(3, 1, asdecimal=True)


def _string_enum(enum: type[StrEnum], name: str) -> Enum:
    return Enum(
        enum,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=max(len(member.value) for member in enum),
        values_callable=lambda members: [member.value for member in members],
    )


class BrandModel(Base):
    __tablename__ = "brands"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(BRAND_NAME_MAX_LENGTH))
    slug: Mapped[str] = mapped_column(String(SLUG_MAX_LENGTH), unique=True)


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(CATEGORY_NAME_MAX_LENGTH))
    slug: Mapped[str] = mapped_column(String(SLUG_MAX_LENGTH), unique=True)


class SneakerModel(Base):
    __tablename__ = "sneakers"
    __table_args__ = (
        CheckConstraint("base_price >= 0", name="base_price_non_negative"),
        CheckConstraint(
            "(testimonial_quote IS NULL) = (testimonial_author IS NULL)", name="testimonial_complete"
        ),
        Index("ix_sneakers_currency_base_price", "currency", "base_price"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(SNEAKER_NAME_MAX_LENGTH))
    slug: Mapped[str] = mapped_column(String(SLUG_MAX_LENGTH), unique=True)
    description: Mapped[str] = mapped_column(String(SNEAKER_DESCRIPTION_MAX_LENGTH))
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("brands.id", ondelete="RESTRICT"), index=True)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)
    gender: Mapped[Gender] = mapped_column(_string_enum(Gender, "gender"))
    base_price: Mapped[Decimal] = mapped_column(PRICE_TYPE)
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[SneakerStatus] = mapped_column(_string_enum(SneakerStatus, "status"), index=True)
    release_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reference: Mapped[str | None] = mapped_column(String(SNEAKER_REFERENCE_MAX_LENGTH), unique=True)
    material: Mapped[str] = mapped_column(String(SPEC_FIELD_MAX_LENGTH), server_default="")
    technology: Mapped[str] = mapped_column(String(SPEC_FIELD_MAX_LENGTH), server_default="")
    weight: Mapped[str] = mapped_column(String(SPEC_FIELD_MAX_LENGTH), server_default="")
    cushioning: Mapped[str] = mapped_column(String(SPEC_FIELD_MAX_LENGTH), server_default="")
    usage: Mapped[str] = mapped_column(String(SNEAKER_USAGE_MAX_LENGTH), server_default="")
    testimonial_quote: Mapped[str | None] = mapped_column(String(TESTIMONIAL_QUOTE_MAX_LENGTH))
    testimonial_author: Mapped[str | None] = mapped_column(String(TESTIMONIAL_AUTHOR_MAX_LENGTH))

    colorways: Mapped[list[ColorwayModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ColorwayModel.name",
    )
    images: Mapped[list[SneakerImageModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SneakerImageModel.position",
    )


class ColorwayModel(Base):
    __tablename__ = "colorways"
    __table_args__ = (CheckConstraint("price_override >= 0", name="price_override_non_negative"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    sneaker_id: Mapped[UUID] = mapped_column(ForeignKey("sneakers.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(COLORWAY_NAME_MAX_LENGTH))
    color_code: Mapped[str] = mapped_column(String(7))
    sku: Mapped[str] = mapped_column(String(SKU_MAX_LENGTH), unique=True)
    price_override: Mapped[Decimal | None] = mapped_column(PRICE_TYPE)

    sizes: Mapped[list[SizeVariantModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SizeVariantModel.size",
    )


class SizeVariantModel(Base):
    __tablename__ = "size_variants"
    __table_args__ = (
        UniqueConstraint("colorway_id", "size", name="uq_size_variants_colorway_id_size"),
        CheckConstraint("stock >= 0", name="stock_non_negative"),
        CheckConstraint("size > 0", name="size_positive"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    colorway_id: Mapped[UUID] = mapped_column(ForeignKey("colorways.id", ondelete="CASCADE"), index=True)
    size: Mapped[Decimal] = mapped_column(SIZE_TYPE)
    stock: Mapped[int]


class SneakerImageModel(Base):
    __tablename__ = "sneaker_images"
    __table_args__ = (CheckConstraint("position >= 0", name="position_non_negative"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    sneaker_id: Mapped[UUID] = mapped_column(ForeignKey("sneakers.id", ondelete="CASCADE"), index=True)
    public_id: Mapped[str] = mapped_column(String(IMAGE_PUBLIC_ID_MAX_LENGTH))
    url: Mapped[str] = mapped_column(String(IMAGE_URL_MAX_LENGTH))
    alt: Mapped[str] = mapped_column(String(IMAGE_ALT_MAX_LENGTH))
    position: Mapped[int]
    is_primary: Mapped[bool]
