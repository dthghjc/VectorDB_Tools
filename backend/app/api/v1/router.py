from fastapi import APIRouter

from app.api.v1.endpoints.auth.router import router as auth_router
from app.api.v1.endpoints.keys.router import router as keys_router
from app.api.v1.endpoints.connections.router import router as connections_router

api_router = APIRouter()

# 包含认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# 包含密钥管理路由
api_router.include_router(keys_router, prefix="/keys", tags=["api-keys"])

# 包含 Milvus 连接管理路由
api_router.include_router(connections_router, prefix="/connections", tags=["milvus-connections"])
