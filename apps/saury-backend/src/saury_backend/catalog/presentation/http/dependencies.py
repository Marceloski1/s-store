from typing import Annotated

from fastapi import Depends
from shared.presentation.http.dependencies import SessionDep

from saury_backend.catalog.domain.repositories.brand_repository import BrandRepository
from saury_backend.catalog.domain.repositories.category_repository import CategoryRepository
from saury_backend.catalog.infrastructure.persistence.brand_repository import SqlAlchemyBrandRepository
from saury_backend.catalog.infrastructure.persistence.category_repository import SqlAlchemyCategoryRepository


def get_brand_repository(session: SessionDep) -> BrandRepository:
    return SqlAlchemyBrandRepository(session)


def get_category_repository(session: SessionDep) -> CategoryRepository:
    return SqlAlchemyCategoryRepository(session)


BrandRepositoryDep = Annotated[BrandRepository, Depends(get_brand_repository)]
CategoryRepositoryDep = Annotated[CategoryRepository, Depends(get_category_repository)]
