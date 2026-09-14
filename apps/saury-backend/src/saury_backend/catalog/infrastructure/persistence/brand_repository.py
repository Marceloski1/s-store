from uuid import UUID

from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from saury_backend.catalog.domain.entities.brand import Brand
from saury_backend.catalog.infrastructure.persistence.models import BrandModel


class SqlAlchemyBrandRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, brand: Brand) -> None:
        await self._session.merge(BrandModel(id=brand.id, name=brand.name, slug=brand.slug.value))

    async def get(self, brand_id: UUID) -> Brand | None:
        model = await self._session.get(BrandModel, brand_id)
        return _to_entity(model) if model is not None else None

    async def get_by_slug(self, slug: Slug) -> Brand | None:
        model = await self._session.scalar(select(BrandModel).where(BrandModel.slug == slug.value))
        return _to_entity(model) if model is not None else None

    async def paginate(self, params: PageParams) -> Page[Brand]:
        total = await self._session.scalar(select(func.count()).select_from(BrandModel)) or 0
        models = await self._session.scalars(
            select(BrandModel).order_by(BrandModel.name, BrandModel.id).offset(params.offset).limit(params.size)
        )
        return Page(items=[_to_entity(model) for model in models], total=total, page=params.page, size=params.size)

    async def delete(self, brand: Brand) -> None:
        model = await self._session.get(BrandModel, brand.id)
        if model is not None:
            await self._session.delete(model)


def _to_entity(model: BrandModel) -> Brand:
    return Brand(id=model.id, name=model.name, slug=Slug(model.slug))
