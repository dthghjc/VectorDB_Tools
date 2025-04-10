import os
from pydantic import HttpUrl, SecretStr, computed_field, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    # Tell BaseSettings to load variables from .env file
    # And handle case insensitivity for environment variables
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False, # Environment variables are often uppercase
        extra='ignore' # Ignore extra env vars not defined in the model
    )

    # MySQL
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: SecretStr # BaseSettings handles SecretStr automatically
    mysql_db: str

    # OpenAI
    openai_api_key: SecretStr # BaseSettings handles SecretStr automatically
    openai_base_url: HttpUrl # BaseSettings handles HttpUrl automatically

    # BGE (Optional)
    bge_api_key: Optional[SecretStr] = None # Use None as default for Optional fields
    bge_base_url: Optional[HttpUrl] = None

    # Gradio
    gradio_username: str
    gradio_password: SecretStr # BaseSettings handles SecretStr automatically
    gradio_port: int = 7860 # Provide default value directly

    # Milvus Connection
    milvus_host: str = 'localhost' # Provide default value directly
    milvus_port: int = 19530 # Provide default value directly
    milvus_token: Optional[SecretStr] = None # Add MILVUS_TOKEN from your .env example

    # Database URL (constructed using computed_field)
    @computed_field
    @property
    def database_url(self) -> str:
        # BaseSettings ensures required fields are present before computed_field runs
        password = self.mysql_password.get_secret_value()
        return f"mysql+mysqlconnector://{self.mysql_user}:{password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"

# No need for a separate load_config function
# Just instantiate the class where needed: config = Settings()

# Example usage (optional, for testing)
if __name__ == "__main__":
    import sys
    try:
        config = Settings()
        print("\nConfiguration loaded successfully via BaseSettings:")
        # Use model_dump() in Pydantic V2
        print(config.model_dump(exclude={'mysql_password', 'openai_api_key', 'bge_api_key', 'gradio_password', 'milvus_token'}))
        print(f"Database URL: {config.database_url}")
        # Access secrets safely
        if config.openai_api_key:
             print(f"OpenAI Key starts with: {config.openai_api_key.get_secret_value()[:5]}...")
        else:
             print("OpenAI Key is not set.")
        if config.milvus_token:
             print(f"Milvus Token is set.")
        else:
             print("Milvus Token is not set.")
    except Exception as e: # Catch potential validation errors during instantiation
        print(f"\nFailed to load configuration: {e}", file=sys.stderr)
        sys.exit(1) 