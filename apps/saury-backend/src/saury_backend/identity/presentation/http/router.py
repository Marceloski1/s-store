from fastapi import APIRouter

from saury_backend.identity.presentation.http.auth import router as auth_router
from saury_backend.identity.presentation.http.users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
