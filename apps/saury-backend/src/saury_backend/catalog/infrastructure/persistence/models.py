from uuid import UUID

from shared.domain.slug import SLUG_MAX_LENGTH
from shared.infrastructure.persistence.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from saury_backend.catalog.domain.entities.brand import BRAND_NAME_MAX_LENGTH
from saury_backend.catalog.domain.entities.category import CATEGORY_NAME_MAX_LENGTH


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
