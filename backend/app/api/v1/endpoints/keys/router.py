# backend/app/api/v1/endpoints/keys/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.crypto import get_public_key
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.crypto import RSAPublicKeyResponse

router = APIRouter()

@router.get("/public-key", summary="获取 RSA 公钥", response_model=RSAPublicKeyResponse)
async def get_rsa_public_key(
    current_user: User = Depends(get_current_active_user)
) -> RSAPublicKeyResponse:
    """
    获取 RSA 公钥
    
    需要用户认证。前端在提交 API Key 之前需要调用此接口获取公钥进行加密。
    
    Args:
        current_user: 当前认证的用户
        
    Returns:
        包含 PEM 格式公钥的响应
        
    Raises:
        HTTPException: 当公钥获取失败时
    """
    try:
        public_key_pem = get_public_key()
        
        return RSAPublicKeyResponse(public_key=public_key_pem)
        
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"加密系统未就绪: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取公钥失败: {e}"
        )

# 未来在这里添加 API Key CRUD 端点
# @router.post("/", summary="创建 API Key")
# @router.get("/", summary="获取用户的 API Key 列表") 
# @router.put("/{key_id}", summary="更新 API Key")
# @router.delete("/{key_id}", summary="删除 API Key")
