from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMClient(ABC):
    """
    所有 Embedding 客户端必须遵循的抽象基类 (接口).
    """
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def create_embeddings(self, texts: List[str], options: Dict[str, Any]) -> List[List[float]]:
        """
        接收一个文本列表，为每个文本生成一个 embedding 向量。

        Args:
            texts: 需要被向量化的字符串列表。
            options: 其他参数, e.g., {"model": "text-embedding-3-small"}

        Returns:
            一个包含多个 embedding 向量的列表, e.g., [[0.1, 0.2, ...], [0.3, 0.4, ...]]
        """
        pass