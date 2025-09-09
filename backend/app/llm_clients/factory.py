# 这个文件不需要任何改动！
# 这正是工厂模式的强大之处，它不关心客户端具体执行什么任务。

from .base import LLMClient
from .openai_client import OpenAIClient
from .ollama_client import OllamaClient
from .baidu_qianfan_client import BaiduQianfanClient

class LLMClientFactory:
    _clients = {
        "openai": OpenAIClient,
        "siliconflow": OpenAIClient,
        "ollama": OllamaClient,
        "bce-qianfan": BaiduQianfanClient,
    }

    @classmethod
    def get_client(cls, provider: str, api_key: str | None = None, base_url: str | None = None) -> LLMClient:
        provider_key = provider.lower().replace(" ", "-")
        client_class = cls._clients.get(provider_key)

        if not client_class:
            supported = list(cls._clients.keys())
            raise ValueError(f"Unsupported LLM provider: '{provider}'. Supported providers are: {supported}")

        return client_class(api_key=api_key, base_url=base_url)