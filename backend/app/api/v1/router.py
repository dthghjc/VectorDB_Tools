from fastapi import APIRouter

from app.api.v1.endpoints.auth.router import router as auth_router

api_router = APIRouter()

# 包含认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
