from datetime import datetime
from sqlalchemy import func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# --- 1. 使用 SQLAlchemy 2.0 风格的声明式基类 ---
# 你项目中的所有模型 (Model) 都应该继承自这个 Base 类。
class Base(DeclarativeBase):
    pass


# --- 2. 创建一个可重用的 Mixin 类用于自动生成时间戳 ---
class TimestampMixin:
    """
    一个 Mixin 类，为模型提供 created_at 和 updated_at 时间戳字段。

    - 使用数据库的 `TIMESTAMP WITH TIME ZONE` 类型，确保时区正确。
    - 时间戳的生成和更新完全由数据库在服务端完成，保证数据一致性。
    """

    # 使用 Mapped 和 mapped_column 进行现代化的类型注解。
    # DateTime(timezone=True) 会在 PostgreSQL 中创建 TIMESTAMPTZ (TIMESTAMP WITH TIME ZONE) 类型的列。
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # 使用数据库函数 func.now() 作为服务器端默认值
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # 同样设置一个服务器端默认值
        onupdate=func.now(),       # 在记录更新时，也使用数据库函数 func.now()
        nullable=False
    )