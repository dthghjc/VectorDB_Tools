import secrets
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, Field

class Settings(BaseSettings):
    """
    使用 Pydantic BaseSettings 来管理应用配置。
    它会自动从 .env 文件和环境变量中读取配置项。
    """
    # --- 数据库基础配置 ---
    # Pydantic 会自动读取这些环境变量，并进行类型转换
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # --- 通过计算字段，动态构建完整的数据库连接 URL ---
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        构建 SQLAlchemy 的数据库连接字符串。
        """
        # 注意：这里我们硬编码了 'postgresql+psycopg2' 和 '?sslmode=require'
        # 如果未来需要更灵活的配置，也可以将它们加入到环境变量中
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode=require"
        )
    
    # JWT 配置
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))  # 环境变量优先，否则自动生成
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时 = 1440分钟

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 创建一个全局唯一的 settings 实例，供整个应用导入和使用
settings = Settings()
