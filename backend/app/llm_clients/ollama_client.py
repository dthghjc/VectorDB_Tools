import ollama
from ollama import OllamaError
from .base import LLMClient
from typing import List, Dict, Any, Tuple

class OllamaClient(LLMClient):
    """Ollama Embedding 的具体实现"""
    def validate_api_key(self) -> Tuple[bool, str]:
        try:
            client = ollama.Client(host=self.base_url)
            client.models.list()
            return True, f"Successfully connected to Ollama at {self.base_url or 'default host'}."
        except OllamaError as e:
            # 捕获连接失败等特定请求错误
            return False, f"Failed to connect to Ollama at {self.base_url or 'default host'}. Is the service running? Error: {e.cause}"
        except Exception as e:
            # 捕获其他未知异常
            return False, f"An unexpected error occurred while connecting to Ollama: {e}"

        
    def create_embeddings(self, texts: List[str], options: Dict[str, Any]) -> List[List[float]]:
        client = ollama.Client(host=self.base_url)
        
        model = options.get("model")
        if not model:
            raise ValueError("'model' option is required for Ollama Embedding.")

        try:
            # Ollama SDK 需要逐个处理文本，我们用列表推导式来批量完成
            return [client.embeddings(model=model, prompt=text)['embedding'] for text in texts]
        except Exception as e:
            print(f"Error calling Ollama embedding API: {e}")
            raise