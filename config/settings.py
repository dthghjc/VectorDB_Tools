import os
from pydantic import HttpUrl, SecretStr, computed_field, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

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

    # MySQL
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: SecretStr = SecretStr("")
    mysql_db: str

    # OpenAI
    openai_api_key: SecretStr
    openai_base_url: str = 'https://api.openai.com/v1'  # 默认值为 OpenAI API 的基础 URL

    # BGE (Optional)
    bge_api_key: Optional[SecretStr] = None
    bge_base_url: Optional[HttpUrl] = None

    # Gradio
    gradio_username: str
    gradio_password: SecretStr
    gradio_port: int = 7860

    # Milvus Connection
    milvus_host: str = 'localhost'
    milvus_port: int = 19530
    milvus_token: Optional[SecretStr] = None

    # 使用 computed_field 构建的数据库 URL
    @computed_field
    @property
    def database_url(self) -> str:
        # 由于使用了 BaseSettings，在计算 database_url 之前，所有必需的字段（mysql_user、mysql_password、mysql_host、mysql_port、mysql_db）都已经被验证和加载
        password = self.mysql_password.get_secret_value()
        return f"mysql+mysqlconnector://{self.mysql_user}:{password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"

# 配置加载说明:
# 1. 直接实例化 Settings 类即可获取配置
# 2. 所有配置项会自动从 .env 文件加载
# 3. 敏感信息(密码、API密钥等)使用 SecretStr 类型自动加密
# 4. 可选配置项使用 Optional 类型并设置默认值为 None
# 5. 数据库 URL 通过 computed_field 装饰器自动构建