import qianfan
from .base import LLMClient
from typing import List, Dict, Any

class BaiduQianfanClient(LLMClient):
    """百度千帆 Embedding 模型的具体实现"""
    
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        super().__init__(api_key, base_url)
        # 约定 api_key 格式: "your_api_key:your_secret_key"
        try:
            self.ak, self.sk = (self.api_key or ':').split(':', 1)
            if not self.ak or not self.sk:
                raise ValueError
        except (ValueError, IndexError):
            raise ValueError("Baidu Qianfan API key format is invalid. Expected 'api_key:secret_key'.")

    def create_embeddings(self, texts: List[str], options: Dict[str, Any]) -> List[List[float]]:
        model = options.get("model")
        if not model:
            # 例如 "Embedding-V1" 或 "bge-large-zh"
            raise ValueError("'model' option is required for BaiduQianfanClient Embedding.")
            
        try:
            # 使用 AK/SK 初始化 Embedding 服务
            embedding_service = qianfan.Embedding(ak=self.ak, sk=self.sk)
            
            resp = embedding_service.do(
                model=model,
                texts=texts
            )
            
            # 从响应体中提取 embedding 列表
            return [item['embedding'] for item in resp.body['data']]
        except Exception as e:
            print(f"Error calling Baidu Qianfan embedding API: {e}")
            raise