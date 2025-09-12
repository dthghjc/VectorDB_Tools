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
    敏感信息（用户名、密码）采用前端 RSA 加密 + 后端 AES 对称加密的双重保护。
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
    host: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="Milvus 服务器主机地址，如 'localhost' 或 'milvus.example.com'"
    )
    
    port: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        server_default="19530",  # Milvus 默认端口
        comment="Milvus 服务器端口，默认 19530"
    )
    
    database_name: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True,
        comment="Milvus 数据库名称，可选（Milvus 2.0+ 支持多数据库）"
    )
    
    # 认证信息 - 敏感信息（加密存储）
    encrypted_username: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True,
        comment="使用 AES 对称加密存储的用户名（如果启用了认证）"
    )
    
    encrypted_password: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True,
        comment="使用 AES 对称加密存储的密码（如果启用了认证）"
    )
    
    username_preview: Mapped[str | None] = mapped_column(
        String(50), 
        nullable=True,
        comment="用户名的安全预览格式，如 'admin****'"
    )
    
    # 连接配置
    secure: Mapped[bool] = mapped_column(
        server_default="false",
        nullable=False,
        comment="是否使用 TLS/SSL 安全连接"
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
        # 端口范围约束
        CheckConstraint(
            "port > 0 AND port <= 65535", 
            name='ck_milvus_connection_port_range'
        ),
    )
    
    # 关系映射
    user = relationship("User", back_populates="milvus_connections")
    
    def generate_username_preview(self, username: str) -> str:
        """
        生成用户名的安全预览格式
        
        Args:
            username: 原始用户名
            
        Returns:
            安全预览字符串，格式：前3位****
        """
        if not username or len(username) < 4:
            return "****"
        return f"{username[:3]}****"
    
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
        return bool(self.encrypted_username and self.encrypted_password)
    
    def get_connection_string(self) -> str:
        """
        生成连接字符串用于显示（不包含敏感信息）
        
        Returns:
            格式：host:port[/database] (secure/insecure)
        """
        conn_str = f"{self.host}:{self.port}"
        if self.database_name:
            conn_str += f"/{self.database_name}"
        conn_str += f" ({'secure' if self.secure else 'insecure'})"
        return conn_str
    
    def __repr__(self) -> str:
        return f"<MilvusConnection(id={self.id}, name='{self.name}', host='{self.host}', port={self.port}, status='{self.status}')>"
