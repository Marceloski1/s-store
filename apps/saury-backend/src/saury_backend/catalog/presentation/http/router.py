from fastapi import APIRouter

from saury_backend.catalog.presentation.http.brands import router as brands_router
from saury_backend.catalog.presentation.http.categories import router as categories_router
from saury_backend.catalog.presentation.http.colorways import router as colorways_router
from saury_backend.catalog.presentation.http.images import router as images_router
from saury_backend.catalog.presentation.http.sneakers import router as sneakers_router
from saury_backend.catalog.presentation.http.storefront import router as storefront_router

router = APIRouter()
router.include_router(brands_router)
router.include_router(categories_router)
router.include_router(sneakers_router)
router.include_router(colorways_router)
router.include_router(images_router)
router.include_router(storefront_router)
