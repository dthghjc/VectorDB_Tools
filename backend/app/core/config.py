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
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None

    # --- 通过计算字段，动态构建完整的数据库连接 URL ---
    @computed_field
    @property
    def DATABASE_URL(self) -> Optional[str]:
        """
        构建 SQLAlchemy 的数据库连接字符串。
        如果数据库配置不完整，返回 None。
        """
        if not all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.DB_NAME]):
            return None
            
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
    
    # RSA 密钥配置
    RSA_PRIVATE_KEY: Optional[str] = None
    RSA_PUBLIC_KEY: Optional[str] = None
    
    # AES 加密配置
    AES_ENCRYPTION_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    def validate_crypto_keys(self) -> None:
        """
        验证加密密钥配置完整性
        如果缺失必要密钥则抛出详细错误信息
        """
        missing_keys = []
        
        if not self.RSA_PRIVATE_KEY:
            missing_keys.append("RSA_PRIVATE_KEY")
        if not self.RSA_PUBLIC_KEY:
            missing_keys.append("RSA_PUBLIC_KEY") 
        if not self.AES_ENCRYPTION_KEY:
            missing_keys.append("AES_ENCRYPTION_KEY")
            
        if missing_keys:
            keys_str = "、".join(missing_keys)
            error_msg = f"""❌ 缺少必要的加密密钥配置：{keys_str}

🔧 请按以下步骤生成并配置所有密钥：
   1. 在 backend 目录运行: ./generate-keys.sh
   2. 复制输出的三行密钥到 backend/.env 文件
   3. 重新启动应用

💡 如果已配置密钥但仍出现此错误，请检查：
   - backend/.env 文件是否存在
   - 所有三个密钥是否正确设置
   - 密钥值是否用双引号包裹"""
            
            raise ValueError(error_msg)

# 创建一个全局唯一的 settings 实例，供整个应用导入和使用
settings = Settings()
