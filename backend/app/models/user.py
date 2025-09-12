# backend/app/models/user.py

from sqlalchemy import Integer, String, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
# 1. 导入 PostgreSQL 特定的 UUID 类型
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),          # 使用 UUID 类型, as_uuid=True 确保 Python 侧处理为 UUID 对象
        primary_key=True,
        server_default=text("gen_random_uuid()"), # 3. 让数据库自动生成 UUID
        index=True
    )
    
    full_name: Mapped[str | None] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    
    # 关系映射 - 一个用户可以有多个 API Key 和 Milvus 连接
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    milvus_connections = relationship("MilvusConnection", back_populates="user", cascade="all, delete-orphan")