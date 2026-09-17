from uuid import UUID

from shared.domain.money import Money
from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug
from sqlalchemy import ColumnElement, Select, and_, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from saury_backend.catalog.domain.entities.colorway import Colorway
from saury_backend.catalog.domain.entities.image import Image
from saury_backend.catalog.domain.entities.size_variant import SizeVariant
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerFilters, SneakerSort
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.infrastructure.persistence.models import (
    BrandModel,
    CategoryModel,
    ColorwayModel,
    SizeVariantModel,
    SneakerImageModel,
    SneakerModel,
)

_LIKE_ESCAPE = "\\"


class SqlAlchemySneakerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, sneaker: Sneaker) -> None:
        model = await self._session.get(SneakerModel, sneaker.id)
        if model is None:
            model = SneakerModel(id=sneaker.id)
            self._session.add(model)
        _apply_sneaker(model, sneaker)
        await self._session.flush()

    async def get(self, sneaker_id: UUID) -> Sneaker | None:
        model = await self._session.get(SneakerModel, sneaker_id)
        return _to_sneaker(model) if model is not None else None

    async def get_by_slug(self, slug: Slug) -> Sneaker | None:
        model = await self._session.scalar(select(SneakerModel).where(SneakerModel.slug == slug.value))
        return _to_sneaker(model) if model is not None else None

    async def find_sku_owner(self, sku: str) -> UUID | None:
        return await self._session.scalar(select(ColorwayModel.sneaker_id).where(ColorwayModel.sku == sku))

    async def paginate(self, filters: SneakerFilters, params: PageParams) -> Page[Sneaker]:
        conditions = _conditions(filters)
        total = await self._session.scalar(select(func.count()).select_from(SneakerModel).where(*conditions)) or 0
        query = _ordered(select(SneakerModel).where(*conditions), filters)
        models = await self._session.scalars(query.offset(params.offset).limit(params.size))
        return Page(items=[_to_sneaker(model) for model in models], total=total, page=params.page, size=params.size)

    async def delete(self, sneaker: Sneaker) -> None:
        model = await self._session.get(SneakerModel, sneaker.id)
        if model is not None:
            await self._session.delete(model)

    async def exists_for_brand(self, brand_id: UUID) -> bool:
        return bool(await self._session.scalar(select(exists().where(SneakerModel.brand_id == brand_id))))

    async def exists_for_category(self, category_id: UUID) -> bool:
        return bool(await self._session.scalar(select(exists().where(SneakerModel.category_id == category_id))))


def _conditions(filters: SneakerFilters) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []
    if filters.brand is not None:
        conditions.append(
            SneakerModel.brand_id.in_(select(BrandModel.id).where(BrandModel.slug == filters.brand.value))
        )
    if filters.category is not None:
        conditions.append(
            SneakerModel.category_id.in_(select(CategoryModel.id).where(CategoryModel.slug == filters.category.value))
        )
    if filters.gender is not None:
        conditions.append(SneakerModel.gender == filters.gender)
    if filters.status is not None:
        conditions.append(SneakerModel.status == filters.status)
    if filters.price_currency is not None:
        conditions.append(SneakerModel.currency == filters.price_currency)
    if filters.min_price is not None:
        conditions.append(SneakerModel.base_price >= filters.min_price.amount)
    if filters.max_price is not None:
        conditions.append(SneakerModel.base_price <= filters.max_price.amount)
    if filters.size is not None or filters.in_stock:
        conditions.append(_has_matching_size(filters))
    if filters.q is not None:
        pattern = f"%{_escape_like(filters.q)}%"
        conditions.append(
            or_(
                SneakerModel.name.ilike(pattern, escape=_LIKE_ESCAPE),
                SneakerModel.description.ilike(pattern, escape=_LIKE_ESCAPE),
            )
        )
    return conditions


def _has_matching_size(filters: SneakerFilters) -> ColumnElement[bool]:
    size_conditions: list[ColumnElement[bool]] = [ColorwayModel.sneaker_id == SneakerModel.id]
    if filters.size is not None:
        size_conditions.append(SizeVariantModel.size == filters.size.value)
    if filters.in_stock:
        size_conditions.append(SizeVariantModel.stock > 0)
    return exists(
        select(SizeVariantModel.id)
        .join(ColorwayModel, SizeVariantModel.colorway_id == ColorwayModel.id)
        .where(and_(*size_conditions))
    )


def _ordered(query: Select[tuple[SneakerModel]], filters: SneakerFilters) -> Select[tuple[SneakerModel]]:
    columns = {
        SneakerSort.NAME: [SneakerModel.name],
        SneakerSort.PRICE: [SneakerModel.currency, SneakerModel.base_price],
        SneakerSort.RELEASE_DATE: [SneakerModel.release_date],
        SneakerSort.CREATED_AT: [SneakerModel.created_at],
    }[filters.sort]
    ordering = [column.desc() if filters.descending else column.asc() for column in columns]
    if filters.sort is SneakerSort.RELEASE_DATE:
        ordering = [ordering[0].nulls_last()]
    return query.order_by(*ordering, SneakerModel.id)


def _escape_like(value: str) -> str:
    return value.replace(_LIKE_ESCAPE, _LIKE_ESCAPE * 2).replace("%", f"{_LIKE_ESCAPE}%").replace("_", f"{_LIKE_ESCAPE}_")


def _apply_sneaker(model: SneakerModel, sneaker: Sneaker) -> None:
    model.name = sneaker.name
    model.slug = sneaker.slug.value
    model.description = sneaker.description
    model.brand_id = sneaker.brand_id
    model.category_id = sneaker.category_id
    model.gender = sneaker.gender
    model.base_price = sneaker.base_price.amount
    model.currency = sneaker.base_price.currency
    model.status = sneaker.status
    model.release_date = sneaker.release_date
    model.created_at = sneaker.created_at
    model.updated_at = sneaker.updated_at
    existing_colorways = {colorway.id: colorway for colorway in model.colorways}
    model.colorways = [
        _apply_colorway(existing_colorways.get(colorway.id) or ColorwayModel(id=colorway.id), colorway)
        for colorway in sneaker.colorways
    ]
    existing_images = {image.id: image for image in model.images}
    model.images = [
        _apply_image(existing_images.get(image.id) or SneakerImageModel(id=image.id), image) for image in sneaker.images
    ]


def _apply_colorway(model: ColorwayModel, colorway: Colorway) -> ColorwayModel:
    model.name = colorway.name
    model.color_code = colorway.color_code
    model.sku = colorway.sku
    model.price_override = colorway.price_override.amount if colorway.price_override else None
    existing_sizes = {variant.id: variant for variant in model.sizes}
    model.sizes = [
        _apply_size(existing_sizes.get(variant.id) or SizeVariantModel(id=variant.id), variant)
        for variant in colorway.sizes
    ]
    return model


def _apply_size(model: SizeVariantModel, variant: SizeVariant) -> SizeVariantModel:
    model.size = variant.size.value
    model.stock = variant.stock
    return model


def _apply_image(model: SneakerImageModel, image: Image) -> SneakerImageModel:
    model.public_id = image.public_id
    model.url = image.url
    model.alt = image.alt
    model.position = image.position
    model.is_primary = image.is_primary
    return model


def _to_sneaker(model: SneakerModel) -> Sneaker:
    return Sneaker(
        id=model.id,
        name=model.name,
        slug=Slug(model.slug),
        description=model.description,
        brand_id=model.brand_id,
        category_id=model.category_id,
        gender=model.gender,
        base_price=Money(model.base_price, model.currency),
        status=model.status,
        release_date=model.release_date,
        created_at=model.created_at,
        updated_at=model.updated_at,
        colorways=[_to_colorway(colorway, model.currency) for colorway in model.colorways],
        images=[_to_image(image) for image in model.images],
    )


def _to_colorway(model: ColorwayModel, currency: str) -> Colorway:
    return Colorway(
        id=model.id,
        name=model.name,
        color_code=model.color_code,
        sku=model.sku,
        price_override=Money(model.price_override, currency) if model.price_override is not None else None,
        sizes=[SizeVariant(id=size.id, size=ShoeSize(size.size), stock=size.stock) for size in model.sizes],
    )


def _to_image(model: SneakerImageModel) -> Image:
    return Image(
        id=model.id,
        public_id=model.public_id,
        url=model.url,
        alt=model.alt,
        position=model.position,
        is_primary=model.is_primary,
    )
