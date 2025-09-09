from .base import LLMClient
from .openai_client import OpenAIClient
from .baidu_qianfan_client import BaiduQianfanClient
from .ollama_client import OllamaClient

class LLMClientFactory:
    # 1. 定义哪些客户端由 OpenAIClient 处理
    _OPENAI_COMPATIBLE_PROVIDERS = {"openai", "siliconflow", "nvidia-nim"}
    
    # 2. 为这些兼容的客户端提供各自的“验证说明书”
    _VALIDATION_CONFIGS = {
        "openai": {
            "method": "list_models"
        },
        "siliconflow": {
            "method": "embedding",
            "test_model": "BAAI/bge-large-zh-v1.5" # 硅基流动的测试模型
        },
        "nvidia-nim": {
            "method": "embedding",
            "test_model": "baai/bge-m3" # NVIDIA NIM 的测试模型
        },
    }
    
    # 3. 特殊的客户端类
    _clients = {
        "bce-qianfan": BaiduQianfanClient,
        "ollama": OllamaClient,
    }

    @classmethod
    def get_client(cls, provider: str, api_key: str | None = None, base_url: str | None = None) -> LLMClient:
        provider_key = provider.lower().replace(" ", "-")

        # 4. 智能决策逻辑
        if provider_key in cls._OPENAI_COMPATIBLE_PROVIDERS:
            client_class = OpenAIClient
            # 从“说明书”中为该 provider 查找配置
            validation_config = cls._VALIDATION_CONFIGS.get(provider_key)
            # 创建实例时，注入配置
            return client_class(
                api_key=api_key,
                base_url=base_url,
                validation_config=validation_config
            )

        client_class = cls._clients.get(provider_key)
        if client_class:
            # 对于其他独立客户端，正常创建
            return client_class(api_key=api_key, base_url=base_url)

        raise ValueError(f"Unsupported LLM provider: '{provider_key}'.")