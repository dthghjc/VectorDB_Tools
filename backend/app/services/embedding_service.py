# app/services/embedding_service.py

from app.llm_clients.factory import LLMClientFactory

# 准备要向量化的文本
input_texts = [
    "今天天气真好，适合出去玩。",
    "如何学习人工智能？",
    "Gemini is a powerful AI model."
]

# --- 示例 1: 调用 OpenAI ---
openai_client = LLMClientFactory.get_client("openai", api_key="sk-...")
embeddings = openai_client.create_embeddings(
    texts=input_texts, 
    options={"model": "text-embedding-3-small"}
)
print(f"OpenAI: Got {len(embeddings)} embeddings, first one has {len(embeddings[0])} dimensions.")


# --- 示例 2: 调用 硅基流动 ---
siliconflow_client = LLMClientFactory.get_client(
    provider="siliconflow",
    api_key="sk-...",
    base_url="https://api.siliconflow.cn/v1"
)
embeddings = siliconflow_client.create_embeddings(
    texts=input_texts, 
    options={"model": "alibaba/bge-large-zh-v1.5"} # 使用硅基流动支持的模型
)
print(f"SiliconFlow: Got {len(embeddings)} embeddings, first one has {len(embeddings[0])} dimensions.")


# --- 示例 3: 调用 百度千帆 ---
qianfan_client = LLMClientFactory.get_client(
    provider="bce-qianfan",
    api_key="your_api_key:your_secret_key"
)
embeddings = qianfan_client.create_embeddings(
    texts=input_texts, 
    options={"model": "Embedding-V1"} # 使用百度千帆的Embedding模型
)
print(f"Baidu Qianfan: Got {len(embeddings)} embeddings, first one has {len(embeddings[0])} dimensions.")


# --- 示例 4: 调用 Ollama ---
ollama_client = LLMClientFactory.get_client(
    provider="ollama",
    base_url="http://localhost:11434"
)
embeddings = ollama_client.create_embeddings(
    texts=input_texts, 
    options={"model": "mxbai-embed-large"} # 使用你本地下载的embedding模型
)
print(f"Ollama: Got {len(embeddings)} embeddings, first one has {len(embeddings[0])} dimensions.")