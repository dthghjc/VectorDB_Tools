# backend/app/services/api_key_service.py

from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import logging
from sqlalchemy.orm import Session

from app.crud.api_key import api_key_crud
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyUpdate
from app.llm_clients.factory import LLMClientFactory

logger = logging.getLogger(__name__)


class ApiKeyServiceError(Exception):
    """API Key 服务专用异常"""
    def __init__(self, message: str, error_code: str = "API_KEY_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ApiKeyService:
    """
    API Key 管理服务
    
    职责：
    1. API Key 的 CRUD 业务逻辑
    2. API Key 验证和状态管理
    3. 使用统计和报告
    
    遵循 Linus 哲学：
    - 简洁的接口：每个方法只做一件事
    - 统一的错误处理：消除特殊情况
    - 实用主义：解决实际问题
    """
    
    def create_api_key(
        self,
        *,
        user_id: UUID,
        api_key_data: ApiKeyCreate,
        db: Session
    ) -> Dict[str, Any]:
        """
        创建新的 API Key
        
        Args:
            user_id: 用户 ID
            api_key_data: API Key 创建数据
            db: 数据库会话
            
        Returns:
            创建的 API Key 信息（不包含敏感数据）
            
        Raises:
            ApiKeyServiceError: 创建失败时
        """
        try:
            # 检查名称是否重复
            existing_key = api_key_crud.get_by_name(
                db=db, name=api_key_data.name, user_id=user_id
            )
            if existing_key:
                raise ApiKeyServiceError(
                    f"API Key 名称 '{api_key_data.name}' 已存在",
                    "DUPLICATE_NAME"
                )
            
            # 创建 API Key
            api_key_obj = api_key_crud.create(
                db=db, obj_in=api_key_data, user_id=user_id
            )
            
            # 返回安全信息
            return self._format_api_key_response(api_key_obj)
            
        except ApiKeyServiceError:
            raise
        except Exception as e:
            logger.error(f"创建 API Key 失败: {e}", exc_info=True)
            raise ApiKeyServiceError(
                f"创建 API Key 失败: {str(e)}",
                "CREATE_ERROR"
            )
    
    def get_user_api_keys(
        self,
        *,
        user_id: UUID,
        db: Session,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取用户的 API Key 列表
        
        Args:
            user_id: 用户 ID
            db: 数据库会话
            provider: 过滤服务提供商
            status: 过滤状态
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            包含 API Key 列表和总数的字典
        """
        try:
            api_keys, total = api_key_crud.get_multi(
                db=db,
                user_id=user_id,
                provider=provider,
                status=status,
                skip=skip,
                limit=limit
            )
            
            return {
                "items": [self._format_api_key_response(key) for key in api_keys],
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"获取用户 API Key 列表失败: {e}", exc_info=True)
            raise ApiKeyServiceError(
                f"获取 API Key 列表失败: {str(e)}",
                "GET_LIST_ERROR"
            )
    
    def get_api_key(
        self,
        *,
        api_key_id: UUID,
        user_id: UUID,
        db: Session
    ) -> Dict[str, Any]:
        """
        获取单个 API Key 信息
        
        Args:
            api_key_id: API Key ID
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            API Key 信息
        """
        try:
            api_key_obj = api_key_crud.get(db=db, id=api_key_id, user_id=user_id)
            if not api_key_obj:
                raise ApiKeyServiceError(
                    f"API Key 不存在或您无权访问: {api_key_id}",
                    "NOT_FOUND"
                )
            
            return self._format_api_key_response(api_key_obj)
            
        except ApiKeyServiceError:
            raise
        except Exception as e:
            logger.error(f"获取 API Key 失败: {e}", exc_info=True)
            raise ApiKeyServiceError(
                f"获取 API Key 失败: {str(e)}",
                "GET_ERROR"
            )
    
    def update_api_key(
        self,
        *,
        api_key_id: UUID,
        user_id: UUID,
        update_data: ApiKeyUpdate,
        db: Session
    ) -> Dict[str, Any]:
        """
        更新 API Key
        
        Args:
            api_key_id: API Key ID
            user_id: 用户 ID
            update_data: 更新数据
            db: 数据库会话
            
        Returns:
            更新后的 API Key 信息
        """
        try:
            # 获取现有 API Key
            api_key_obj = api_key_crud.get(db=db, id=api_key_id, user_id=user_id)
            if not api_key_obj:
                raise ApiKeyServiceError(
                    f"API Key 不存在或您无权访问: {api_key_id}",
                    "NOT_FOUND"
                )
            
            # 检查名称重复（如果要更新名称）
            if update_data.name and update_data.name != api_key_obj.name:
                existing_key = api_key_crud.get_by_name(
                    db=db, name=update_data.name, user_id=user_id
                )
                if existing_key:
                    raise ApiKeyServiceError(
                        f"API Key 名称 '{update_data.name}' 已存在",
                        "DUPLICATE_NAME"
                    )
            
            # 更新 API Key
            updated_key = api_key_crud.update(
                db=db, db_obj=api_key_obj, obj_in=update_data
            )
            
            return self._format_api_key_response(updated_key)
            
        except ApiKeyServiceError:
            raise
        except Exception as e:
            logger.error(f"更新 API Key 失败: {e}", exc_info=True)
            raise ApiKeyServiceError(
                f"更新 API Key 失败: {str(e)}",
                "UPDATE_ERROR"
            )
    
    def delete_api_key(
        self,
        *,
        api_key_id: UUID,
        user_id: UUID,
        db: Session
    ) -> bool:
        """
        删除 API Key
        
        Args:
            api_key_id: API Key ID
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            是否删除成功
        """
        try:
            success = api_key_crud.delete(db=db, id=api_key_id, user_id=user_id)
            if not success:
                raise ApiKeyServiceError(
                    f"API Key 不存在或您无权删除: {api_key_id}",
                    "NOT_FOUND"
                )
            
            logger.info(f"成功删除 API Key: {api_key_id}")
            return True
            
        except ApiKeyServiceError:
            raise
        except Exception as e:
            logger.error(f"删除 API Key 失败: {e}", exc_info=True)
            raise ApiKeyServiceError(
                f"删除 API Key 失败: {str(e)}",
                "DELETE_ERROR"
            )
    
    def validate_api_key(
        self,
        *,
        api_key_id: UUID,
        user_id: UUID,
        db: Session
    ) -> Tuple[bool, str]:
        """
        验证 API Key 是否有效
        
        Args:
            api_key_id: API Key ID
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            (是否有效, 验证信息)
        """
        try:
            # 获取 API Key
            api_key_obj = api_key_crud.get(db=db, id=api_key_id, user_id=user_id)
            if not api_key_obj:
                return False, "API Key 不存在或您无权访问"
            
            if not api_key_obj.is_active():
                return False, "API Key 已被禁用"
            
            # 获取明文密钥
            plaintext_key = api_key_crud.get_plaintext_key(
                encrypted_key=api_key_obj.encrypted_api_key
            )
            
            # 创建客户端并验证
            client = LLMClientFactory.get_client(
                provider=api_key_obj.provider,
                api_key=plaintext_key,
                base_url=api_key_obj.base_url
            )
            
            is_valid, message = client.validate_api_key()
            
            if is_valid:
                logger.info(f"API Key 验证成功: {api_key_obj.name}")
            else:
                logger.warning(f"API Key 验证失败: {api_key_obj.name}, 原因: {message}")
            
            return is_valid, message
            
        except Exception as e:
            logger.error(f"API Key 验证过程中发生错误: {e}", exc_info=True)
            return False, f"验证过程中发生错误: {str(e)}"
    
    def get_user_stats(
        self,
        *,
        user_id: UUID,
        db: Session
    ) -> Dict[str, Any]:
        """
        获取用户 API Key 统计信息
        
        Args:
            user_id: 用户 ID
            db: 数据库会话
            
        Returns:
            统计信息字典
        """
        try:
            stats = api_key_crud.get_user_stats(db=db, user_id=user_id)
            return stats
            
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {e}", exc_info=True)
            raise ApiKeyServiceError(
                f"获取统计信息失败: {str(e)}",
                "STATS_ERROR"
            )
    
    def _format_api_key_response(self, api_key_obj: ApiKey) -> Dict[str, Any]:
        """
        格式化 API Key 响应数据（安全格式，不包含敏感信息）
        
        Args:
            api_key_obj: API Key 数据库对象
            
        Returns:
            格式化的响应数据
        """
        return {
            "id": api_key_obj.id,                # 保持 UUID 类型
            "user_id": api_key_obj.user_id,      # 添加缺失的 user_id
            "name": api_key_obj.name,
            "provider": api_key_obj.provider,
            "base_url": api_key_obj.base_url,
            "key_preview": api_key_obj.key_preview,
            "status": api_key_obj.status,
            "last_used_at": api_key_obj.last_used_at,  # 保持 datetime 类型
            "usage_count": api_key_obj.usage_count,
            "created_at": api_key_obj.created_at,      # 保持 datetime 类型
            "updated_at": api_key_obj.updated_at       # 保持 datetime 类型
        }


# 全局服务实例
api_key_service = ApiKeyService()
