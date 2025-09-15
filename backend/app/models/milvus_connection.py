# backend/app/models/milvus_connection.py

from sqlalchemy import String, Integer, Text, ForeignKey, text, UniqueConstraint, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from .base import Base, TimestampMixin

class MilvusConnection(Base, TimestampMixin):
    """
    Milvus 连接配置模型
    
    用于存储用户的 Milvus 数据库连接信息。
    敏感信息（认证 token）采用前端 RSA 加密 + 后端 AES 对称加密的双重保护。
    """
    __tablename__ = "milvus_connections"

    # 主键 - 使用 UUID
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True
    )
    
    # 关联用户 - 每个连接配置必须属于一个用户
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),  # 用户删除时级联删除连接配置
        nullable=False,
        index=True
    )
    
    # 基本信息字段
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True,
        comment="连接配置的用户自定义名称，如 'Production Milvus' 或 'Test Environment'"
    )
    
    description: Mapped[str | None] = mapped_column(
        String(500), 
        nullable=True,
        comment="连接配置的描述信息"
    )
    
    # 连接参数 - 非敏感信息（明文存储）
    uri: Mapped[str] = mapped_column(
        String(500), 
        nullable=False,
        comment="Milvus 连接 URI，完整地址包含协议和端口，如 'http://localhost:19530' 或 'https://cluster.vectordb.zillizcloud.com'"
    )
    
    database_name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="Milvus 数据库名称（必填）"
    )
    
    # 认证信息
    encrypted_token: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        comment="使用 AES 对称加密存储的认证 token（必填，格式：token 或 username:password）"
    )
    
    
    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20), 
        server_default="'active'",
        nullable=False,
        index=True,
        comment="连接状态：active(启用) 或 inactive(禁用)"
    )
    
    # 使用统计
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后一次使用该连接的时间"
    )
    
    usage_count: Mapped[int] = mapped_column(
        Integer, 
        server_default="0", 
        nullable=False,
        comment="连接的累计使用次数"
    )
    
    # 测试相关字段
    last_tested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后一次测试该连接的时间"
    )
    
    test_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="最后一次测试状态：success(成功) 或 failed(失败)"
    )
    
    test_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="最后一次测试的详细信息或错误消息"
    )
    
    test_response_time: Mapped[float | None] = mapped_column(
        nullable=True,
        comment="最后一次测试的响应时间（毫秒）"
    )
    
    # 数据库约束
    __table_args__ = (
        # 同一用户下的连接名称不能重复
        UniqueConstraint('user_id', 'name', name='uq_user_milvus_connection_name'),
        # 状态字段约束
        CheckConstraint(
            "status IN ('active', 'inactive')", 
            name='ck_milvus_connection_status'
        ),
    )
    
    # 关系映射
    user = relationship("User", back_populates="milvus_connections")
    
    
    def update_last_used(self) -> None:
        """
        更新最后使用时间和使用次数
        调用此方法后需要手动提交数据库事务
        """
        self.last_used_at = datetime.utcnow()
        self.usage_count += 1
    
    def update_test_result(self, success: bool, message: str, response_time: float | None = None) -> None:
        """
        更新测试结果
        
        Args:
            success: 测试是否成功
            message: 测试消息
            response_time: 响应时间（毫秒），可选
        """
        self.last_tested_at = datetime.utcnow()
        self.test_status = "success" if success else "failed"
        self.test_message = message
        self.test_response_time = response_time
    
    def is_active(self) -> bool:
        """检查连接配置是否处于启用状态"""
        return self.status == "active"
    
    def has_authentication(self) -> bool:
        """检查是否配置了认证信息"""
        return bool(self.encrypted_token)
    
    def get_connection_string(self) -> str:
        """
        生成连接字符串用于显示（不包含敏感信息）
        
        Returns:
            格式：uri[/database]
        """
        conn_str = self.uri
        if self.database_name:
            conn_str += f"/{self.database_name}"
        return conn_str
    
    def __repr__(self) -> str:
        return f"<MilvusConnection(id={self.id}, name='{self.name}', uri='{self.uri}', status='{self.status}')>"
