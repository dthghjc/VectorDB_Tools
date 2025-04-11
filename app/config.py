import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
from pydantic import ConfigDict

# 加载 .env 文件
load_dotenv()

class Settings(BaseSettings):
    # 告诉BaseSettings从.env文件加载变量
    # 并处理环境变量的大小写不敏感
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False, # 环境变量通常是大写的
        extra='ignore' # 忽略未在模型中定义的额外环境变量
    )

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL")

    # BGE
    BGE_API_KEY: Optional[str] = os.getenv("BGE_API_KEY")
    BGE_BASE_URL: Optional[str] = os.getenv("BGE_BASE_URL")

    # Milvus
    MILVUS_HOST: str = os.getenv("MILVUS_HOST")
    MILVUS_PORT: int = os.getenv("MILVUS_PORT")
    MILVUS_TOKEN: Optional[str] = os.getenv("MILVUS_TOKEN")

    # MySQL
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = os.getenv("MYSQL_PORT")
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB: str = os.getenv("MYSQL_DB")

    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    @property
    def get_database_url(self) -> str:
        """
        获取适用于 SQLAlchemy 的数据库连接 URL
        """
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        else:
            return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"



Config = Settings()