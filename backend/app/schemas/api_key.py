# backend/app/schemas/api_key.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ApiProvider(str, Enum):
    """API 服务提供商枚举"""
    OPENAI = "openai"
    SILICONFLOW = "siliconflow"
    BCE_QIANFAN = "bce-qianfan"
    NVIDIA_NIM = "nvidia-nim"
    OLLAMA = "ollama"


class ApiKeyBase(BaseModel):
    """API Key 基础模式"""
    name: str = Field(..., min_length=1, max_length=255, description="API Key 名称")
    provider: ApiProvider = Field(..., description="服务提供商")
    base_url: str = Field(..., min_length=1, max_length=500, description="API 基础 URL")


class ApiKeyCreate(ApiKeyBase):
    """创建 API Key 请求模式"""
    encrypted_api_key: str = Field(..., description="前端 RSA 加密后的 API Key")


class ApiKeyUpdate(BaseModel):
    """更新 API Key 请求模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="API Key 名称")
    provider: Optional[ApiProvider] = Field(None, description="服务提供商")
    base_url: Optional[str] = Field(None, min_length=1, max_length=500, description="API 基础 URL")
    status: Optional[str] = Field(None, pattern="^(active|inactive)$", description="API Key 状态")


class ApiKeyInDB(ApiKeyBase):
    """数据库中的 API Key 模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    key_preview: str = Field(..., description="API Key 安全预览")
    status: str = Field(..., description="API Key 状态")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")
    usage_count: int = Field(0, description="使用次数")
    # 测试相关字段
    last_tested_at: Optional[datetime] = Field(None, description="最后测试时间")
    test_status: Optional[str] = Field(None, description="测试状态")
    test_message: Optional[str] = Field(None, description="测试消息")
    test_response_time: Optional[float] = Field(None, description="测试响应时间(ms)")
    created_at: datetime
    updated_at: datetime


class ApiKeyResponse(ApiKeyInDB):
    """API Key 响应模式（客户端返回）"""
    pass


class ApiKeyList(BaseModel):
    """API Key 列表响应"""
    items: list[ApiKeyResponse]
    total: int
    page: int
    size: int
    pages: int


class ApiKeyCreateResponse(BaseModel):
    """创建 API Key 成功响应"""
    id: UUID
    name: str
    provider: str
    base_url: str
    key_preview: str
    status: str
    usage_count: int
    created_at: datetime
    updated_at: datetime
    message: str = "API Key 创建成功"


class ApiKeyTestRequest(BaseModel):
    """测试 API Key 请求"""
    test_endpoint: Optional[str] = Field(None, description="测试端点路径")


class ApiKeyTestResponse(BaseModel):
    """测试 API Key 响应"""
    success: bool
    message: str
    response_time_ms: Optional[float] = None
    tested_at: Optional[datetime] = None
    status_code: Optional[int] = None


class ApiProviderListResponse(BaseModel):
    """API 供应商列表响应"""
    providers: list[str] = Field(..., description="支持的API供应商列表")
