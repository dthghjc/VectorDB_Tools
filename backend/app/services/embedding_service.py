# backend/app/services/embedding_service.py

from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import logging
from sqlalchemy.orm import Session

from app.llm_clients.factory import LLMClientFactory
from app.llm_clients.base import LLMClient
from app.crud.api_key import api_key_crud
from app.models.api_key import ApiKey
from app.core.db import get_db

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """嵌入服务专用异常"""
    def __init__(self, message: str, error_code: str = "EMBEDDING_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class EmbeddingService:
    """
    嵌入服务核心类
    
    职责：
    1. 管理用户的 API Key 和 LLM 客户端
    2. 提供统一的文本向量化接口
    3. 处理错误和使用统计
    
    设计原则（Linus 哲学）：
    - 简洁的数据结构：只存储必要的状态
    - 消除特殊情况：统一的错误处理机制
    - 实用主义：解决实际问题，不搞过度设计
    """
    
    def __init__(self):
        """
        初始化嵌入服务
        
        注意：不在构造函数中存储数据库连接或客户端实例
        每次操作都是无状态的，避免状态管理的复杂性
        """
        pass
    
    def create_embeddings(
        self,
        *,
        texts: List[str],
        api_key_id: UUID,
        user_id: UUID,
        model: str,
        db: Session,
        options: Optional[Dict[str, Any]] = None
    ) -> List[List[float]]:
        """
        为文本列表生成嵌入向量
        
        Args:
            texts: 需要向量化的文本列表
            api_key_id: 用户选择的 API Key ID
            user_id: 用户 ID（用于权限验证）
            model: 模型名称
            db: 数据库会话
            options: 额外选项，如 batch_size 等
            
        Returns:
            嵌入向量列表，每个向量是 float 列表
            
        Raises:
            EmbeddingError: 当发生任何错误时
        """
        if not texts:
            raise EmbeddingError("文本列表不能为空", "EMPTY_TEXTS")
        
        if not model.strip():
            raise EmbeddingError("模型名称不能为空", "EMPTY_MODEL")
        
        try:
            # 1. 获取并验证 API Key
            api_key_obj = self._get_validated_api_key(
                db=db, 
                api_key_id=api_key_id, 
                user_id=user_id
            )
            
            # 2. 获取明文 API Key 和客户端
            client = self._get_llm_client(db=db, api_key_obj=api_key_obj)
            
            # 3. 准备参数
            embedding_options = {"model": model}
            if options:
                embedding_options.update(options)
            
            # 4. 生成嵌入向量
            embeddings = client.create_embeddings(texts, embedding_options)
            
            # 5. 更新使用统计
            self._update_usage_stats(db=db, api_key_obj=api_key_obj)
            
            logger.info(
                f"成功生成 {len(texts)} 个文本的嵌入向量，"
                f"用户: {user_id}, API Key: {api_key_obj.name}"
            )
            
            return embeddings
            
        except EmbeddingError:
            # 重新抛出已知的嵌入错误
            raise
        except Exception as e:
            # 包装未知错误
            logger.error(f"嵌入生成失败: {e}", exc_info=True)
            raise EmbeddingError(
                f"嵌入生成过程中发生未知错误: {str(e)}", 
                "UNKNOWN_ERROR"
            )
    
    def validate_api_key(
        self,
        *,
        api_key_id: UUID,
        user_id: UUID,
        db: Session
    ) -> Tuple[bool, str]:
        """
        验证用户的 API Key 是否可用
        
        Args:
            api_key_id: API Key ID
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            (是否有效, 验证信息)
        """
        try:
            # 1. 获取并验证 API Key
            api_key_obj = self._get_validated_api_key(
                db=db, 
                api_key_id=api_key_id, 
                user_id=user_id
            )
            
            # 2. 获取客户端并验证
            client = self._get_llm_client(db=db, api_key_obj=api_key_obj)
            
            # 3. 调用客户端验证方法
            is_valid, message = client.validate_api_key()
            
            if is_valid:
                logger.info(f"API Key 验证成功: {api_key_obj.name}")
            else:
                logger.warning(f"API Key 验证失败: {api_key_obj.name}, 原因: {message}")
            
            return is_valid, message
            
        except EmbeddingError as e:
            return False, e.message
        except Exception as e:
            logger.error(f"API Key 验证过程中发生错误: {e}", exc_info=True)
            return False, f"验证过程中发生错误: {str(e)}"
    
    def get_available_models(
        self,
        *,
        api_key_id: UUID,
        user_id: UUID,
        db: Session
    ) -> List[str]:
        """
        获取指定 API Key 支持的模型列表
        
        Args:
            api_key_id: API Key ID
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            支持的模型名称列表
        """
        try:
            # 获取并验证 API Key
            api_key_obj = self._get_validated_api_key(
                db=db, 
                api_key_id=api_key_id, 
                user_id=user_id
            )
            
            # 根据提供商返回支持的模型
            provider_models = {
                "openai": [
                    "text-embedding-3-small",
                    "text-embedding-3-large", 
                    "text-embedding-ada-002"
                ],
                "siliconflow": [
                    "BAAI/bge-large-zh-v1.5",
                    "BAAI/bge-small-zh-v1.5",
                    "sentence-transformers/all-MiniLM-L6-v2"
                ],
                "nvidia-nim": [
                    "baai/bge-m3",
                    "nvidia/nv-embed-v1"
                ],
                "bce-qianfan": [
                    "embedding-v1",
                    "bge-large-zh"
                ],
                "ollama": [
                    "nomic-embed-text",
                    "all-minilm",
                    "snowflake-arctic-embed"
                ]
            }
            
            return provider_models.get(api_key_obj.provider.lower(), [])
            
        except EmbeddingError:
            raise
        except Exception as e:
            logger.error(f"获取模型列表失败: {e}", exc_info=True)
            raise EmbeddingError(
                f"获取模型列表失败: {str(e)}", 
                "GET_MODELS_ERROR"
            )
    
    def _get_validated_api_key(
        self, 
        *, 
        db: Session, 
        api_key_id: UUID, 
        user_id: UUID
    ) -> ApiKey:
        """
        获取并验证 API Key
        
        这是一个内部方法，消除了所有特殊情况：
        - 不存在
        - 无权限 
        - 已禁用
        
        统一抛出 EmbeddingError，调用者无需处理不同的错误类型
        """
        # 获取 API Key
        api_key_obj = api_key_crud.get(db=db, id=api_key_id, user_id=user_id)
        if not api_key_obj:
            raise EmbeddingError(
                f"API Key 不存在或您无权访问: {api_key_id}", 
                "API_KEY_NOT_FOUND"
            )
        
        # 检查状态
        if not api_key_obj.is_active():
            raise EmbeddingError(
                f"API Key 已被禁用: {api_key_obj.name}", 
                "API_KEY_DISABLED"
            )
        
        return api_key_obj
    
    def _get_llm_client(self, *, db: Session, api_key_obj: ApiKey) -> LLMClient:
        """
        根据 API Key 获取对应的 LLM 客户端
        
        Args:
            db: 数据库会话
            api_key_obj: API Key 数据库对象
            
        Returns:
            配置好的 LLM 客户端实例
        """
        try:
            # 解密获取明文 API Key
            plaintext_key = api_key_crud.get_plaintext_key(
                encrypted_key=api_key_obj.encrypted_api_key
            )
            
            # 使用工厂创建客户端
            client = LLMClientFactory.get_client(
                provider=api_key_obj.provider,
                api_key=plaintext_key,
                base_url=api_key_obj.base_url
            )
            
            return client
            
        except ValueError as e:
            # 工厂不支持该提供商
            raise EmbeddingError(
                f"不支持的服务提供商: {api_key_obj.provider}", 
                "UNSUPPORTED_PROVIDER"
            )
        except Exception as e:
            # 其他错误（解密失败等）
            raise EmbeddingError(
                f"无法创建 LLM 客户端: {str(e)}", 
                "CLIENT_CREATION_ERROR"
            )
    
    def _update_usage_stats(self, *, db: Session, api_key_obj: ApiKey) -> None:
        """
        更新 API Key 使用统计
        
        Args:
            db: 数据库会话
            api_key_obj: API Key 对象
        """
        try:
            api_key_crud.update_usage(db=db, db_obj=api_key_obj)
        except Exception as e:
            # 使用统计更新失败不应该影响主要功能
            # 记录日志但不抛出异常
            logger.warning(f"更新 API Key 使用统计失败: {e}")


# 全局服务实例
embedding_service = EmbeddingService()
