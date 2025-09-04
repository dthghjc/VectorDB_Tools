# backend/app/api/v1/endpoints/keys/router.py

from fastapi import APIRouter, Depends
from app.core.crypto import get_public_key
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/public-key", summary="获取 RSA 公钥")
async def get_rsa_public_key(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取 RSA 公钥
    
    需要用户认证。前端在提交 API Key 之前需要调用此接口获取公钥进行加密。
    
    Args:
        current_user: 当前认证的用户
        
    Returns:
        包含 PEM 格式公钥的响应
    """
    try:
        public_key_pem = get_public_key()
        
        return {
            "success": True,
            "data": {
                "public_key": public_key_pem,
                "algorithm": "RSA-OAEP",
                "key_size": 2048,
                "usage": "encrypt_api_keys"
            },
            "message": "RSA 公钥获取成功"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取公钥失败: {str(e)}",
            "data": None
        }

# 未来在这里添加 API Key CRUD 端点
# @router.post("/", summary="创建 API Key")
# @router.get("/", summary="获取用户的 API Key 列表") 
# @router.put("/{key_id}", summary="更新 API Key")
# @router.delete("/{key_id}", summary="删除 API Key")
