# backend/app/schemas/milvus_connection.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, validator


class MilvusConnectionBase(BaseModel):
    """Milvus 连接配置基础模式"""
    name: str = Field(..., min_length=1, max_length=255, description="连接配置名称")
    description: Optional[str] = Field(None, max_length=500, description="连接配置描述")
    host: str = Field(..., min_length=1, max_length=255, description="Milvus 服务器主机地址")
    port: int = Field(19530, ge=1, le=65535, description="Milvus 服务器端口")
    database_name: Optional[str] = Field(None, max_length=255, description="数据库名称（可选）")
    secure: bool = Field(False, description="是否使用 TLS/SSL 安全连接")


class MilvusConnectionCreate(MilvusConnectionBase):
    """创建 Milvus 连接请求模式"""
    encrypted_username: Optional[str] = Field(None, description="前端 RSA 加密后的用户名（可选）")
    encrypted_password: Optional[str] = Field(None, description="前端 RSA 加密后的密码（可选）")
    
    @validator('encrypted_password')
    def validate_auth_pair(cls, v, values):
        """验证认证信息必须成对出现"""
        username = values.get('encrypted_username')
        if bool(username) != bool(v):
            raise ValueError('用户名和密码必须同时提供或同时为空')
        return v


class MilvusConnectionUpdate(BaseModel):
    """更新 Milvus 连接请求模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="连接配置名称")
    description: Optional[str] = Field(None, max_length=500, description="连接配置描述")
    host: Optional[str] = Field(None, min_length=1, max_length=255, description="Milvus 服务器主机地址")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Milvus 服务器端口")
    database_name: Optional[str] = Field(None, max_length=255, description="数据库名称")
    secure: Optional[bool] = Field(None, description="是否使用 TLS/SSL 安全连接")
    status: Optional[str] = Field(None, pattern="^(active|inactive)$", description="连接状态")


class MilvusConnectionInDB(MilvusConnectionBase):
    """数据库中的 Milvus 连接模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    username_preview: Optional[str] = Field(None, description="用户名安全预览")
    status: str = Field(..., description="连接状态")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")
    usage_count: int = Field(0, description="使用次数")
    # 测试相关字段
    last_tested_at: Optional[datetime] = Field(None, description="最后测试时间")
    test_status: Optional[str] = Field(None, description="测试状态")
    test_message: Optional[str] = Field(None, description="测试消息")
    test_response_time: Optional[float] = Field(None, description="测试响应时间(ms)")
    created_at: datetime
    updated_at: datetime


class MilvusConnectionResponse(MilvusConnectionInDB):
    """Milvus 连接响应模式（客户端返回）"""
    connection_string: str = Field(..., description="连接字符串（不含敏感信息）")


class MilvusConnectionList(BaseModel):
    """Milvus 连接列表响应"""
    items: list[MilvusConnectionResponse]
    total: int
    page: int
    size: int
    pages: int


class MilvusConnectionCreateResponse(BaseModel):
    """创建 Milvus 连接成功响应"""
    id: UUID
    name: str
    description: Optional[str]
    host: str
    port: int
    database_name: Optional[str]
    username_preview: Optional[str]
    secure: bool
    status: str
    usage_count: int
    connection_string: str
    created_at: datetime
    updated_at: datetime
    message: str = "Milvus 连接配置创建成功"


class MilvusConnectionTestRequest(BaseModel):
    """测试 Milvus 连接请求"""
    timeout_seconds: Optional[int] = Field(10, ge=1, le=60, description="连接超时时间（秒）")


class MilvusConnectionTestResponse(BaseModel):
    """测试 Milvus 连接响应"""
    success: bool
    message: str
    response_time_ms: Optional[float] = None
    tested_at: Optional[datetime] = None
    server_version: Optional[str] = Field(None, description="Milvus 服务器版本")
    collections_count: Optional[int] = Field(None, description="数据库中的集合数量")


class MilvusConnectionStatsResponse(BaseModel):
    """Milvus 连接统计响应"""
    total: int = Field(..., description="总连接数")
    active: int = Field(..., description="活跃连接数")
    inactive: int = Field(..., description="非活跃连接数")
    recently_used: int = Field(..., description="最近使用的连接数（7天内）")
    by_status: dict[str, int] = Field(..., description="按状态分组统计")
    by_secure: dict[str, int] = Field(..., description="按安全连接分组统计")
