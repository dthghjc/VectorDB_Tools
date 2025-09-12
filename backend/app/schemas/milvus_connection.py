# backend/app/schemas/milvus_connection.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, validator
from urllib.parse import urlparse


class MilvusConnectionBase(BaseModel):
    """Milvus 连接配置基础模式"""
    name: str = Field(..., min_length=1, max_length=255, description="连接配置名称")
    description: Optional[str] = Field(None, max_length=500, description="连接配置描述")
    host: str = Field(..., min_length=1, max_length=500, description="Milvus 服务器完整URL（含协议）")
    port: int = Field(19530, ge=1, le=65535, description="Milvus 服务器端口")
    database_name: str = Field(..., min_length=1, max_length=255, description="数据库名称（必填）")
    
    @validator('host')
    def validate_host_url(cls, v):
        """验证主机地址必须是完整的 URL"""
        if not v:
            raise ValueError('主机地址不能为空')
        
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError('主机地址必须是完整的 URL，包含协议（如 http://localhost 或 https://example.com）')
            if parsed.scheme not in ['http', 'https']:
                raise ValueError('协议必须是 http 或 https')
            if parsed.port:
                raise ValueError('请将端口在单独的端口字段中填写，主机地址中不要包含端口')
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f'无效的 URL 格式: {str(e)}')
        
        return v


class MilvusConnectionCreate(MilvusConnectionBase):
    """创建 Milvus 连接请求模式"""
    encrypted_username: str = Field(..., description="前端 RSA 加密后的用户名（必填）")
    encrypted_password: str = Field(..., description="前端 RSA 加密后的密码（必填）")


class MilvusConnectionUpdate(BaseModel):
    """更新 Milvus 连接请求模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="连接配置名称")
    description: Optional[str] = Field(None, max_length=500, description="连接配置描述")
    host: Optional[str] = Field(None, min_length=1, max_length=500, description="Milvus 服务器完整URL")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Milvus 服务器端口")
    database_name: Optional[str] = Field(None, min_length=1, max_length=255, description="数据库名称")
    status: Optional[str] = Field(None, pattern="^(active|inactive)$", description="连接状态")
    
    @validator('host')
    def validate_host_url(cls, v):
        """验证主机地址必须是完整的 URL"""
        if v is None:
            return v
            
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError('主机地址必须是完整的 URL，包含协议（如 http://localhost 或 https://example.com）')
            if parsed.scheme not in ['http', 'https']:
                raise ValueError('协议必须是 http 或 https')
            if parsed.port:
                raise ValueError('请将端口在单独的端口字段中填写，主机地址中不要包含端口')
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f'无效的 URL 格式: {str(e)}')
        
        return v


class MilvusConnectionInDB(MilvusConnectionBase):
    """数据库中的 Milvus 连接模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    username: str = Field(..., description="Milvus 用户名（必填）")
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
    database_name: str
    username: str
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
