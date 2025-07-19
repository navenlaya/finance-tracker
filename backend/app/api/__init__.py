from fastapi import APIRouter
from .auth import router as auth_router
from .plaid import router as plaid_router
from .ml import router as ml_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(plaid_router, prefix="/plaid", tags=["plaid"])
api_router.include_router(ml_router, prefix="/ml", tags=["ml"])
