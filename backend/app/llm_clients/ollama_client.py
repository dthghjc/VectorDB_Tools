import ollama
from .base import LLMClient
from typing import List, Dict, Any

class OllamaClient(LLMClient):
    """Ollama Embedding 的具体实现"""
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