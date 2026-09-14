from fastapi import APIRouter

from saury_backend.catalog.presentation.http.brands import router as brands_router
from saury_backend.catalog.presentation.http.categories import router as categories_router

router = APIRouter()
router.include_router(brands_router)
router.include_router(categories_router)
