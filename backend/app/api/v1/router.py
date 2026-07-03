from fastapi import APIRouter
from app.api.v1.endpoints import documents, search, auth

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(documents.router)
router.include_router(search.router)