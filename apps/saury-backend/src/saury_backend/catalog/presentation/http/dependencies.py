from typing import Annotated

from fastapi import Depends, Request
from shared.presentation.http.dependencies import SessionDep

from saury_backend.catalog.application.ports.image_storage import ImageStorage
from saury_backend.catalog.domain.repositories.brand_repository import BrandRepository
from saury_backend.catalog.domain.repositories.category_repository import CategoryRepository
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerRepository
from saury_backend.catalog.infrastructure.persistence.brand_repository import SqlAlchemyBrandRepository
from saury_backend.catalog.infrastructure.persistence.category_repository import SqlAlchemyCategoryRepository
from saury_backend.catalog.infrastructure.persistence.sneaker_repository import SqlAlchemySneakerRepository
from saury_backend.catalog.infrastructure.storage.cloudinary_image_storage import CloudinaryImageStorage
from saury_backend.config.settings import Settings


def get_brand_repository(session: SessionDep) -> BrandRepository:
    return SqlAlchemyBrandRepository(session)


def get_category_repository(session: SessionDep) -> CategoryRepository:
    return SqlAlchemyCategoryRepository(session)


def get_sneaker_repository(session: SessionDep) -> SneakerRepository:
    return SqlAlchemySneakerRepository(session)


def get_image_storage(request: Request) -> ImageStorage:
    settings: Settings = request.app.state.settings
    api_secret = settings.cloudinary_api_secret
    return CloudinaryImageStorage(
        cloud_name=settings.cloudinary_cloud_name or "",
        api_key=settings.cloudinary_api_key or "",
        api_secret=api_secret.get_secret_value() if api_secret is not None else "",
    )


BrandRepositoryDep = Annotated[BrandRepository, Depends(get_brand_repository)]
CategoryRepositoryDep = Annotated[CategoryRepository, Depends(get_category_repository)]
SneakerRepositoryDep = Annotated[SneakerRepository, Depends(get_sneaker_repository)]
ImageStorageDep = Annotated[ImageStorage, Depends(get_image_storage)]
