from uuid import UUID

from shared.domain.pagination import Page, PageParams
from shared.domain.slug import Slug
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from saury_backend.catalog.domain.entities.category import Category
from saury_backend.catalog.infrastructure.persistence.models import CategoryModel


class SqlAlchemyCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, category: Category) -> None:
        await self._session.merge(CategoryModel(id=category.id, name=category.name, slug=category.slug.value))

    async def get(self, category_id: UUID) -> Category | None:
        model = await self._session.get(CategoryModel, category_id)
        return _to_entity(model) if model is not None else None

    async def get_by_slug(self, slug: Slug) -> Category | None:
        model = await self._session.scalar(select(CategoryModel).where(CategoryModel.slug == slug.value))
        return _to_entity(model) if model is not None else None

    async def paginate(self, params: PageParams) -> Page[Category]:
        total = await self._session.scalar(select(func.count()).select_from(CategoryModel)) or 0
        models = await self._session.scalars(
            select(CategoryModel)
            .order_by(CategoryModel.name, CategoryModel.id)
            .offset(params.offset)
            .limit(params.size)
        )
        return Page(items=[_to_entity(model) for model in models], total=total, page=params.page, size=params.size)

    async def delete(self, category: Category) -> None:
        model = await self._session.get(CategoryModel, category.id)
        if model is not None:
            await self._session.delete(model)


def _to_entity(model: CategoryModel) -> Category:
    return Category(id=model.id, name=model.name, slug=Slug(model.slug))
