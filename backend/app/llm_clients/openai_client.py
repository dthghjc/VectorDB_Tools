from openai import OpenAI, AuthenticationError
from .base import LLMClient
from typing import List, Dict, Any, Tuple

class OpenAIClient(LLMClient):
    """
    OpenAI Embedding API 的具体实现.
    同样适用于 硅基流动 (SiliconFlow)、NVIDIA NIM 等 OpenAI 兼容的 API.
    """
    def __init__(self, api_key: str | None = None, base_url: str | None = None, validation_config: Dict[str, Any] | None = None):
        super().__init__(api_key, base_url)
        # 保存注入的验证配置
        self.validation_config = validation_config or {}
    
    def validate_api_key(self) -> Tuple[bool, str]:
        """
        根据注入的配置动态执行验证。
        """
        method = self.validation_config.get("method")
        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            if method == "list_models":
                # 为 OpenAI 执行 list_models 验证
                client.models.list()
                return True, "API key is valid (validated via list_models)."
            
            elif method == "embedding":
                # 为 NVIDIA / SiliconFlow 执行 embedding 验证
                test_model = self.validation_config.get("test_model")
                if not test_model:
                    return False, "Validation failed: test_model is not configured."
                
                client.embeddings.create(model=test_model, input=["test"])
                return True, "API key is valid (validated via embedding)."
            
            else:
                # 这种情况几乎不会发生，除非在工厂中配置了一个未知的 method 字符串
                return False, f"Validation failed: Unknown validation method '{method}' configured."

        except AuthenticationError as e:
            return False, f"API key is invalid or expired: {e.__cause__}"
        except Exception as e:
            return False, f"An error occurred during validation: {e}"
    
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