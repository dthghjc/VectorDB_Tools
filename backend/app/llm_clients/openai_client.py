from openai import OpenAI
from .base import LLMClient
from typing import List, Dict, Any

class OpenAIClient(LLMClient):
    """
    OpenAI Embedding API 的具体实现.
    同样适用于 硅基流动 (SiliconFlow) 等 OpenAI 兼容的 API.
    """
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