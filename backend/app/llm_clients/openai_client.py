from openai import OpenAI, AuthenticationError
from .base import LLMClient
from typing import List, Dict, Any, Tuple

class OpenAIClient(LLMClient):
    """
    OpenAI Embedding API 的具体实现.
    同样适用于 硅基流动 (SiliconFlow)、NVIDIA NIM 等 OpenAI 兼容的 API.
    """
    def validate_api_key(self) -> Tuple[bool, str]:
        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            client.models.list()
            return True, "API key is valid."
        except AuthenticationError as e:
            # 捕获专门的认证失败异常
            return False, f"API key is invalid or expired: {e.__cause__}"
        except Exception as e:
            # 捕获其他异常，如网络连接问题
            return False, f"An error occurred: {e}"
    
    def create_embeddings(self, texts: List[str], options: Dict[str, Any]) -> List[List[float]]:
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        model = options.get("model")
        if not model:
            raise ValueError("'model' option is required for OpenAI Embedding.")

        try:
            response = client.embeddings.create(
                model=model,
                input=texts
            )
            # 从响应中提取 embedding 列表
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Error calling OpenAI compatible embedding API: {e}")
            raise