import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl, SecretStr
from typing import Optional

# Load environment variables from .env file
# Find the .env file starting from the current directory and going up
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    # Fallback for cases where the script is run from the root directory
    load_dotenv()

class Settings(BaseModel):
    # MySQL
    mysql_host: str = Field(..., env='MYSQL_HOST')
    mysql_port: int = Field(..., env='MYSQL_PORT')
    mysql_user: str = Field(..., env='MYSQL_USER')
    mysql_password: SecretStr = Field(..., env='MYSQL_PASSWORD')
    mysql_db: str = Field(..., env='MYSQL_DB')

    # OpenAI
    openai_api_key: SecretStr = Field(..., env='OPENAI_API_KEY')
    openai_base_url: HttpUrl = Field(..., env='OPENAI_BASE_URL')

    # BGE (Optional - add validation if needed)
    bge_api_key: Optional[SecretStr] = Field(None, env='BGE_API_KEY')
    bge_base_url: Optional[HttpUrl] = Field(None, env='BGE_BASE_URL')

    # Gradio
    gradio_username: str = Field(..., env='GRADIO_USERNAME')
    gradio_password: SecretStr = Field(..., env='GRADIO_PASSWORD')

    # Milvus Connection
    milvus_host: str = Field('localhost', env='MILVUS_HOST')
    milvus_port: int = Field(19530, env='MILVUS_PORT')

    # Database URL (constructed)
    @property
    def database_url(self) -> str:
        # Ensure password is revealed for the URL connection string
        password = self.mysql_password.get_secret_value()
        return f"mysql+mysqlconnector://{self.mysql_user}:{password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        # Allow extra fields if needed, though we define all expected ones
        extra = 'ignore'

def load_config() -> Settings:
    """Loads configuration from environment variables."""
    try:
        settings = Settings()
        return settings
    except Exception as e:
        print(f"Error loading configuration: {e}")
        # Consider raising the exception or exiting if config is critical
        raise ValueError("Configuration could not be loaded. Check your .env file and environment variables.") from e

# Example usage (optional, for testing)
if __name__ == "__main__":
    config = load_config()
    print("Configuration loaded successfully:")
    # Use .dict() carefully, especially with secrets
    print(config.dict(exclude={'mysql_password', 'openai_api_key', 'bge_api_key', 'gradio_password'}))
    print(f"Database URL: {config.database_url}")
    # Access secrets safely
    print(f"OpenAI Key starts with: {config.openai_api_key.get_secret_value()[:5]}...") 