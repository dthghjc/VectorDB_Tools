# backend/app/schemas/crypto.py

from pydantic import BaseModel, Field


class RSAPublicKeyResponse(BaseModel):
    """RSA 公钥响应 - 简化版本"""
    public_key: str = Field(..., description="PEM 格式的 RSA 公钥，用于前端加密 API Key")
