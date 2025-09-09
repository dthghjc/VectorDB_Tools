# backend/app/models/api_key.py

from sqlalchemy import String, Integer, Text, ForeignKey, text, UniqueConstraint, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from .base import Base, TimestampMixin

class ApiKey(Base, TimestampMixin):
    """
    API Key 模型
    
    用于存储用户的第三方服务 API 密钥，如 OpenAI、Google 等。
    密钥采用前端 RSA 加密 + 后端 AES 对称加密的双重保护。
    """
    __tablename__ = "api_keys"

    # 主键 - 使用 UUID
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True
    )
    
    # 关联用户 - 每个 API Key 必须属于一个用户
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),  # 用户删除时级联删除 API Key
        nullable=False,
        index=True
    )
    
    # 基本信息字段
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True,
        comment="API Key 的用户自定义名称，如 'OpenAI GPT-4'"
    )
    
    provider: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        index=True,
        comment="服务提供商，如 'OpenAI', 'Google', 'Anthropic'"
    )
    
    base_url: Mapped[str] = mapped_column(
        String(500), 
        nullable=False,
        comment="API 基础 URL，如 'https://api.openai.com/v1'"
    )
    
    # 密钥安全存储
    encrypted_api_key: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        comment="使用 AES 对称加密存储的完整 API Key"
    )
    
    key_preview: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="API Key 的安全预览格式，如 'sk-proj****...****abcd'"
    )
    
    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20), 
        server_default="'active'",
        nullable=False,
        index=True,
        comment="API Key 状态：active(启用) 或 inactive(禁用)"
    )
    
    # 使用统计
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后一次使用该 API Key 的时间"
    )
    
    usage_count: Mapped[int] = mapped_column(
        Integer, 
        server_default="0", 
        nullable=False,
        comment="API Key 的累计使用次数"
    )
    
    # 测试相关字段
    last_tested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后一次测试该 API Key 的时间"
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
        # 同一用户下的 API Key 名称不能重复
        UniqueConstraint('user_id', 'name', name='uq_user_api_key_name'),
        # 状态字段约束
        CheckConstraint(
            "status IN ('active', 'inactive')", 
            name='ck_api_key_status'
        ),
    )
    
    # 关系映射
    user = relationship("User", back_populates="api_keys")
    
    def generate_key_preview(self, api_key: str) -> str:
        """
        生成 API Key 的安全预览格式
        
        Args:
            api_key: 原始 API Key
            
        Returns:
            安全预览字符串，格式：前6位****...****后4位
        """
        if len(api_key) < 10:
            return "****"
        return f"{api_key[:6]}****...****{api_key[-4:]}"
    
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
        """检查 API Key 是否处于启用状态"""
        return self.status == "active"
    
    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name='{self.name}', provider='{self.provider}', status='{self.status}')>"
