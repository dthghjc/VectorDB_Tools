import qianfan
from qianfan.errors import QianfanError
from .base import LLMClient
from typing import List, Dict, Any, Tuple

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
        
    def validate_api_key(self) -> Tuple[bool, str]:
        try:
            qianfan.Models.list(ak=self.ak, sk=self.sk)
            return True, "Baidu Qianfan AK/SK pair is valid."
        except QianfanError as e:
            # 捕获千帆的特定API异常
            # 常见的认证错误码是 110 (Invalid Access Key Id) 和 111 (Secret Key doesn't match)
            if e.error_code in [110, 111]:
                return False, f"AK or SK is invalid: (code: {e.error_code}) {e.error_msg}"
            return False, f"Qianfan API error: (code: {e.error_code}) {e.error_msg}"
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"
        

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